import random
import abc
import copy
from dataclasses import dataclass
from inspect import signature
from time import perf_counter_ns
from statistics import mean

FORMAT_ACTUAL_VALUE = 0
FORMAT_DELTA_CHANGE = 1
FORMAT_PERCENT_CHANGE = 2
FORMAT_PERCENT_OF_DEFAULT_VALUE = 3

class RandomVariable(abc.ABC):
    def __init__(self, name, address, chance, datatype, default, enabled_on_levels = None, multivar_functions=None):
        # default can always be a list
        if any(type(x) == list for x in [address, datatype]) and not all(type(x) == list for x in [address, datatype, default, multivar_functions]):
            raise TypeError(f'incompatible types of arguments in constructor for {name}')
        if any(type(x) == list for x in [address, datatype]) and \
        not all(x == len(address) for x in [len(address), len(datatype), len(default), len(multivar_functions) + 1]):
            raise ValueError(f'different list lengths in constructor of {name}')
        self.name = name
        self.address = address
        self.default = default
        self.chance = chance
        self.datatype = datatype
        self.value = copy.deepcopy(default)
        self.enabled_on_levels = enabled_on_levels
        self.multivar_functions = multivar_functions
        if type(address) == list:
            self.multivar = True
            self.calculate_value = self.calculate_multivar_value
            self.write_value = self.write_multivar_value
        else:
            self.multivar = False
            self.calculate_value = self.get_randomized_value
            self.write_value = self.write_single_value

    def should_try_to_test(self, level):
        if self.enabled_on_levels:
            return self.enabled_on_levels(level)
        return True
    
    def test(self, random: random.Random, chance, level):
        return random.randint(1, 100) <= chance
    
    @abc.abstractmethod
    def get_randomized_value(self, random: random.Random, level):
        pass

    def calculate_multivar_value(self, random: random.Random, level):
        main_value = self.get_randomized_value(random, level)
        values = [main_value]
        for f in self.multivar_functions:
            sig = signature(f)
            if len(sig.parameters) > 1: # deciding how many params to pass
                values.append(f(main_value, level))
            else:
                values.append(f(main_value))
        return values

    def write_single_value(self, address, value, datatype, WriteMemory):
        try:
            WriteMemory(datatype, value, address)
        except:
            print("error in write_single_value, name=" + str(self.name) + ", value=" + str(value))

    def write_multivar_value(self, addresses, values, datatypes, WriteMemory):
        for i in range(len(addresses)):
            try:
                WriteMemory(datatypes[i], values[i], addresses[i])
            except:
                print("error in write_multivar_value, name=" + str(self.name) + ", value=" + str(values[i]))

    def is_default(self):
        return self.default == self.value
    
    def get_str_value(self, format_type, more_less_words, modify_value_func = None) -> dict:
        val = self.value[0] if self.multivar else self.value
        default = self.default[0] if self.multivar else self.default
        if modify_value_func:
            val = modify_value_func(val)
            default = modify_value_func(default)
        try:
            sign = val >= default
            word = more_less_words[int(not sign)] # first word is increase, second is decrease
            if format_type == FORMAT_ACTUAL_VALUE:
                value_str = str(abs(val))
            elif format_type == FORMAT_DELTA_CHANGE:
                value_str = str(abs(val - default))
            elif format_type == FORMAT_PERCENT_CHANGE:
                value_str = f"{abs(val/default-1):.0%}"
            elif format_type == FORMAT_PERCENT_OF_DEFAULT_VALUE:
                value_str = F"{val/default:.0%}"
            else:
                value_str = "unknown"
            return {'value': value_str, 'sign': '+' if sign else '-', 'change_word': word} 
        except:
            return {'value': f"error in get_str_value for {self.name}, {format_type}", 'sign': '', 'change_word': ''}


    def randomize(self, random, level, WriteMemory, do_write):
        if self.should_try_to_test(level) and self.test(random, self.chance, level):
            value = self.calculate_value(random, level)
        else:
            value = copy.deepcopy(self.default)
        if self.value == value or not do_write:
            return
        self.value = value
        self.write_value(self.address, value, self.datatype, WriteMemory)


class ContinuousVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, min, max, enabled_on_levels = None, multivar_functions=None):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions)
        if min > max:
            (min,max) = (max,min)
        self.min = min
        self.max = max

    def get_randomized_value(self, random: random.Random, level):
        datatype = self.datatype[0] if self.multivar else self.datatype
        if datatype == 'float' or datatype == 'double':
            return random.uniform(self.min, self.max)
        return random.randint(int(self.min), int(self.max))


class DiscreteVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, choices:list, enabled_on_levels = None, multivar_functions=None):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions)
        self.choices = choices

    def get_randomized_value(self, random: random.Random, level):
        return random.choice(self.choices)


class OnOffVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, onValue, enabled_on_levels = None, multivar_functions=None):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions)
        self.onValue = onValue

    def get_randomized_value(self, random: random.Random, level):
        return self.onValue
    
    def get_str_value(self, format_type, more_less_words, modify_value_func = None):
        if self.is_default():
            return {'value': 'Off', 'sign': '', 'change_word': ''}
        return {'value': 'On', 'sign': '', 'change_word': ''}


class OutputStringBase(abc.ABC):
    def __init__(self, format_str: str, modify_value_func = None):
        self.format_str = format_str
        self.modify_value_func = modify_value_func
    
    def is_active(self):
        return True
    
    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class SimpleOutputString(OutputStringBase):
    def __init__(self, value_container, format_str: str, modify_value_func = None):
        super().__init__(format_str, modify_value_func)
        if type(value_container) != list:
            self.value_container = [value_container]
        else:
            self.value_container = value_container

    def __str__(self) -> str:
        if type(self.value_container) != list or (type(self.value_container) == list and len(self.value_container) == 0):
            return f"error in SimpleOutputString __str__, format: {self.format_str}"
        value = self.value_container[0]
        if self.modify_value_func:
            try:
                value = self.modify_value_func(value)
            except:
                print("Error in modify_func_value, value_container = " + self.value_container)
        try:
            return self.format_str.format(value)
        except:
            return f"error in SimpleOutputString format_str.format, format={self.format_str}"


class VarStr(OutputStringBase):
    def __init__(self, var: RandomVariable, format_str: str, format_value_type: int = FORMAT_ACTUAL_VALUE, format_more_less_words=['more', 'less'], modify_value_func = None):
        super().__init__(format_str, modify_value_func)
        self.var = var
        self.format_value_type = format_value_type
        self.format_more_less_words = format_more_less_words

    def is_active(self):
        return not self.var.is_default()
    
    def __str__(self) -> str:
        try:
            return self.format_str.format(**self.var.get_str_value(self.format_value_type, self.format_more_less_words, self.modify_value_func))
        except: 
            return f"error in VarStr format_str.format, format={self.format_str}"

class IndexedStrContainer:
    def __init__(self, name: str, address: int, max_bytes_per_string: int, string_count: int):
        self.name = name
        self.address = address
        self.bytes_per_string = max_bytes_per_string
        self.string_count = string_count
        self.str_dict = dict(zip(range(string_count), ([] for _ in range(string_count))))

    def add_var(self, var: OutputStringBase, indices):
        if type(indices) != list:
            indices = [indices]
        if any(x not in self.str_dict for x in indices):
            raise ValueError(f"wrong index for {self.name} container, indices: {','.join(str(x) for x in indices)}")
        for i in indices:
            self.str_dict[i].append(var)

    def construct_string(self, index: int):
        if index not in self.str_dict:
            string = f"index {index} is not in {self.name} dictionary on construct_string"
            print(string)
        else:
            vars: list[OutputStringBase] = self.str_dict[index]
            str_list = []
            for v in vars:
                if not v.is_active():
                    continue
                str_list.append(str(v))
            string = '\n'.join(str_list)
        return string
    
    def write_string(self, index: int, string: str, WriteMemory):
        if index not in self.str_dict:
            print(f"index {index} is not in {self.name} dictionary in write_string")
            return
        address = self.address + self.bytes_per_string * index
        if len(string) > self.bytes_per_string - 1:
            string = string[:self.bytes_per_string - 1]
        l = list(string.encode('ascii', 'ignore'))
        l.append(0)
        WriteMemory("unsigned char", l, address)

    def update_strings(self, WriteMemory):
        for i in range(self.string_count):
            string = self.construct_string(i)
            self.write_string(i, string, WriteMemory)


class NonIndexedStrContainer:
    def __init__(self, name: str, address: int, max_bytes_per_string: int, string_count: int, n_of_lines_output_address: int):
        self.name = name
        self.address = address
        self.bytes_per_string = max_bytes_per_string
        self.string_count = string_count
        self.n_of_lines_output_address = n_of_lines_output_address
        self.vars = []
        self.n_of_lines_written = 0

    def add_var(self, var: OutputStringBase):
        self.vars.append(var)

    def construct_string(self, var: OutputStringBase):
        if var.is_active():
            return str(var)
        return ""
    
    def write_string(self, index: int, string: str, WriteMemory):
        if index >= self.string_count:
            print(f"Index {index} outside of string_count range for {self.name} in write_string")
            return
        address = self.address + self.bytes_per_string * index
        if len(string) > self.bytes_per_string - 1:
            string = string[:self.bytes_per_string - 1]
        l = list(string.encode('ascii', 'ignore'))
        l.append(0)
        WriteMemory("unsigned char", l, address)
        

    def update_strings(self, WriteMemory):
        free_index = 0
        for v in self.vars:
            if not v.is_active():
                continue
            string = self.construct_string(v)
            self.write_string(free_index, string, WriteMemory)
            free_index = free_index + 1
            if free_index >= self.string_count:
                break
        self.n_of_lines_written = free_index
        self.write_n_of_lines(WriteMemory, free_index, self.n_of_lines_output_address)

    def get_amount_of_lines(self):
        return self.n_of_lines_written
    
    def write_n_of_lines(self, WriteMemory, value, address):
        WriteMemory("int", value, address)


@dataclass
class VarWithStrIndices:
    var_str: OutputStringBase
    plant_indices: list[int] = None
    zombie_indices: list[int] = None
    affects_game_str: bool = False


class RandomVars:
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container: IndexedStrContainer, 
                 zombies_container: IndexedStrContainer, game_container: NonIndexedStrContainer, catZombieHealth: int, cat2: int):
        assert (do_activate_strings and plants_container and zombies_container and game_container) or not do_activate_strings
        self.WriteMemory = write_memory_func
        self.random = random.Random(seed)
        self.do_activate_strings = do_activate_strings
        self.vars: list[VarWithStrIndices] = []
        self.catZombieHealth = catZombieHealth
        self.cat2 = cat2
        self.any_category_enabled = catZombieHealth or cat2 # use to make sure that this object is enabled not just for string rendering
        # we can add categories check here before adding vars, also can adjust their chances
        if self.any_category_enabled:
            self.vars.append(VarWithStrIndices(
                VarStr(
                    var=DiscreteVar("starting sun", 0x0040b09b, chance=self.chance(80, mean([catZombieHealth, cat2])), datatype="int",
                                     default=50, choices=[75, 75, 100], enabled_on_levels=lambda l: l % 5 != 0),
                    format_str="Starting sun amount is {change_word} to {value}",
                    format_value_type=FORMAT_ACTUAL_VALUE,
                    format_more_less_words=['increased', 'decreased']),
                affects_game_str=True
            ))
        if catZombieHealth:
            # special cases are balloon, zomboss. Doesn't change default body health (270), so normals, snorkels, backups, peashooter, squash are untouched
            indices =           [2,   4,   6,   19,   20,   7,   17,  3,    14,   23,   32,   12,   22,   15,   18,   5,   8,    24,   21,   27,  28,   31]
            defaults =          [370, 1100,1100,1350, 450,  1400,100, 500,  500,  3000, 6000, 1350, 850,  500,  500,  150, 500,  70,   500,  1100,500,  2200]
            isArmorHP =         [True,True,True,False,False,True,True,False,False,False,False,False,False,False,False,True,False,False,False,True,False,True]
            changeMultipliers = [1,   0.75,0.75,0.75, 1,    0.75,0.2, 1,    1,    0.5,  0.25, 0.75, 1,    1,    1,    1,   1,    2.75, 0.9,    0.9,   1,    0.6]
            addresses = [0x00522892,0x0052292B,0x00522949,0x0052296E,0x00522A1B,0x00522BB0,0x00522BEF,0x00522CBF,0x00522D64,0x00523D26,0x00523E4A,
                         0x00522DE1,0x00522E8D,0x00522FC7,0x00523300,0x0052337D,0x00523530,0x005235AC,0x0052299C,0x0052382B,0x00523A87,0x0052395D]
            # changeMultipliers modify only 'catZombieHealth*0.05*m' part of calculation, so even with changeMultipliers = 0
            # there still be randomization, just not growing with category change
            assert len(indices) == len(defaults) == len(isArmorHP) == len(changeMultipliers)
            for i in range(len(indices)):
                if isArmorHP[i]:
                    min_m = (0.25 + 0.03 * catZombieHealth) / (defaults[i] / (270 + defaults[i])) * changeMultipliers[i]**0.75
                    max_m = (0.3 + 0.06 * catZombieHealth) / (defaults[i] / (270 + defaults[i])) * changeMultipliers[i]
                else:
                    min_m = (0.25 + 0.03 * catZombieHealth) * changeMultipliers[i]**0.75
                    max_m = (0.3 + 0.06 * catZombieHealth) * changeMultipliers[i]
                args = { 'var': ContinuousVar("zombie health "+str(indices[i]), address=addresses[i], chance=self.chance(120, catZombieHealth), datatype="int",
                                        default=defaults[i], min=max(defaults[i]*(1-min_m), 5), # min has a min value of 5, so it doesn't go negative
                                        max=defaults[i]*(1+max_m)),
                         'format_str': "Health change: {sign}{value}",
                         'format_value_type': FORMAT_PERCENT_CHANGE
                }
                if isArmorHP[i]:
                    args['modify_value_func'] = lambda h:h+270 # body health for zombies with armor
                self.vars.append(VarWithStrIndices(
                    VarStr(**args),
                    zombie_indices=[indices[i]]
                ))
            # ballon has special formatting
            balloon_choices = [40, 60]
            if catZombieHealth > 1:
                balloon_choices.extend([40,60,80])
            if catZombieHealth > 3:
                balloon_choices.extend([60,80,100,100])
            self.vars.append(VarWithStrIndices(
                    VarStr(var=DiscreteVar("zombie health "+str(16), address=0x005234BF, chance=self.chance(120, catZombieHealth), datatype="int",
                                        default=20, choices=balloon_choices),
                            format_str="Balloon requires extra {value} hits to pop",
                            format_value_type=FORMAT_DELTA_CHANGE,
                            modify_value_func=lambda h:h//20 # modify_value_func changes value (and default) before formatting, it doesn't affect actual randomization
                    ),
                    zombie_indices=[16]
            ))
            # dr zomboss has a some chance to just have less hp, and it's printed on screen instead of his tooltip (since he never shows one)
            self.vars.append(VarWithStrIndices(
                    VarStr(var=ContinuousVar("zombie health "+str(25), address=0x00523624, chance=25+catZombieHealth*20, datatype="int",
                                        default=40000, min=27000, max=36000,
                                        enabled_on_levels=lambda l:l==50), # triggered only on 5-10
                            format_str="Zomboss has just {value} of his normal hp",
                            format_value_type=FORMAT_PERCENT_OF_DEFAULT_VALUE,
                    ),
                    affects_game_str=True
            ))
        if do_activate_strings:
            self.plant_strings = plants_container
            self.zombie_strings = zombies_container
            self.game_strings = game_container
            for v in self.vars:
                if v.affects_game_str:
                    self.game_strings.add_var(v.var_str)
                if v.plant_indices:
                    self.plant_strings.add_var(v.var_str, v.plant_indices)
                if v.zombie_indices:
                    self.zombie_strings.add_var(v.var_str, v.zombie_indices)

    def chance(self, base: float, modifier: float) -> float:
        if modifier == 0:
            return 0
        if modifier == 5:
            return base
        # modifier of 5 means use base chance; below 5, chance is decreased exponentially
        return base / (1.4 ** (5 - modifier))

    def randomize(self, level, do_write):
        for v in self.vars:
            v.var_str.var.randomize(self.random, level, self.WriteMemory, do_write)
        if do_write and self.do_activate_strings:
            self.plant_strings.update_strings(self.WriteMemory)
            self.zombie_strings.update_strings(self.WriteMemory)
            self.game_strings.update_strings(self.WriteMemory)