# Intro
In the scope of this library, there are three keyword that need to understand:
1. Fragmentation: The technique or algorithm implemented in this library to slice a string.
2. Fragment: A slice of string, the smallest unit.
3. Fragments: One combination of a sliced string, a unit that contain a list of fragment.

There are three classes in this library as the main interface to use, 2 are what you will probably
use: 
```python
# 2 main module
from slimpy import Fragment, REM
```
and 1 as an output object to simplify accessing result.

There is only one type of exception in slimpy which is a AssertionError, I only implement it to 
assert illegal argument being passed.

## Class: Fragment
It's main purpose is to compute possible combinations of fragments. It is done by slicing a string 
similar to str.split() method but instead using specified character as delimiter, the fragmentation in
this library use the indexes as point of slicing.

To instantiate a Fragment object, you need to pass at least 1 argument, which is a string,
a word that you want to invoke fragmentation on. The algorithm to preform this computation is also part
of the core.py module, fragmentation(), more of it later.
```python
def __init__(self, string: str, delimiter_percentage: float = 0.35, 
             delimiter_limit: Optional[int] = 5):
```
Parameter:
1. string, the string that want to be fragmented.
2. delimiter_percentage, determine how many delimiter will be used, which is determined by multiply the value and 
the length of the string.
3. delimiter_limit, The maximum number of how many delimiter allowed.

#### Warning
If you want to set the delimiter_limit, it is highly advised to set it below 7 as value bigger than 8 may exceed the memory 
capacity of your pc resulting in slow response of your pc. Further development of this library will
address this issue.

```python
# For example, we want to fragment a word "test" with 2 delimiter specification,
string = 'test'
# since 2 delimiter is half it's length so:
percent_delimiter = 0.5
string_Fragment = Fragment(string, percent_delimiter)
# the above code will invoke fragmentation function that equal to:
count_delimiter = percent_delimiter * len(string)
fragmentation(string, count_delimiter)
>>>
{
    3: [
        ['', 'est'], ['t', 'st'], ['te', 't'], ['tes', '']
    ],
    2: [
        ['', '', 'st'], ['', 'e', 't'], ['', 'es', ''],
        ['t', '', 't'], ['t', 's', ''], ['te', '', '']
    ]
}
```
The resulting dictionary from the fragmentation() function can be translated to:
1. The key, a number indicating how many character left after slicing. It further can be translated to 
how many delimiter used (length - the_key).
2. The value, a list consist of combination of possible fragments for the corresponding key.

### Methode
iterate_fragment(): A generator function to iterate fragments
1. Parameters:
   1. re_Pattern (bool): If True, yields a regular expression pattern constructed from fragments. 
   If False, yields a list of fragments.
2. Returns: A generator object that either iterates fragments or a regular expression pattern.

## Class: REM
A class that performs string matching against a reference using regular expressions. A note to make
the class more familiar: the naming is behind abbreviation of Regular Expression Matching.

To instantiate the object, you do not need to pass any argument, though you need to set reference
before perform any matching, we will talk about it soon in the method.

### Methods
- set_reference(): set the reference to match against.
  1. Parameters:
     1. reference: The reference string or an iterable of string. 
  2. Returns: None


- perform_matching(): Performs matching between the Fragment object and the reference.
  1. Parameters:
     1. Frag_obj: A Fragment object from the string to be matched.
     2. case_sensitivity (bool): Flag to indicate if the matching should be 
     case-sensitive or not. Default to True.
  2. Returns: matching result in the form of ReMatchingStatus

## Class: ReMatchingStatus
Class that define matching result and status for ease of use. This object can be used in if else statement.

### Property
1. status: True if it found candidate(s) that match and False otherwise.
2. match: return one match string (str).
3. match_list: return list of matching string(list).
4. pattern: return pattern that match (str).
