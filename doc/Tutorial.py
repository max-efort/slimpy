"""This tutorial will showcase the capability of this library.
We are going to extract information from images of a person id card,
to be more specific we are going to extract name, sex, marital status and job.

Images sample used are inside "images" dir. All are already censored and
preprocessed to yield better result.

(A quick note, the process of censoring the image utilize this library
to find the pixel coordinate of an anchor string to automate the censorship,
but we won't discuss it here, maybe some other time)

If you confused by the code in this tutorial, see the API documentation to know more about
the package
"""
# First let's import the necessary module
from typing import Optional  # for typehint
from pathlib import Path  # for file manipulation
from string import ascii_uppercase as upper  # for string cleanup
import pandas as pd  # to process data
from PIL.Image import open as open_image  # image loader
import pytesseract  # OCR tools used in this tutorial
from slimpy import Fragment, REM  # main player of this tutorial
from re import search, error as rer  # for new class we will define

# If your tesseract executable not in path, first specify the path to it
# pytesseract.pytesseract.tesseract_cmd = path_to_executable\exe_name.exe


# Lets create custom class that can extract fields from image
# the class inherit REM from slimpy
class ExtractFieldWithRegex(REM):
    """
    - A class that show practical application of this package.
      It can extract field(s) from reference (text source).

    - An anchor is given as Fragment object that will be used as boundary rule.

    - A note to keep in mind: when defining boundary rule, extraction do not
      ignore "new line" (no re.DOTALL flag), so a line-break will be act as
      natural boundary if it is not specified.
    ====
    Methode:
    ====
    -   add_rule: Define rule to extract a field.
    -   extract: Perform an extraction.
    -   set_reference: add matching reference.
    ====
    """

    def __init__(self):
        """Instantiate an object to enable creation set of rule to
        use to extract field from text."""
        super().__init__()
        self._rule = {}

    def add_rule(self, field_name,
                 Fragment_start: Optional[Fragment] = None,
                 Fragment_end: Optional[Fragment] = None):
        """
        Adding rule in the form of: {field name: [start boundary, end boundary]}

        :param field_name: Used as key to store a rule to extract a field.
        :param Fragment_start: Fragment object of anchor that mark start of boundary.
        :param Fragment_end: Fragment object of anchor that mark end of boundary.
        """
        assert any([isinstance(Fragment_start, Fragment), isinstance(Fragment_end, Fragment)]), "You " \
            "must pass an argument at least one either to Fragment_start or Fragment_end as an anchor"
        self._rule[field_name] = Fragment_start, Fragment_end

    def perform_extraction(self, case_sensitive=True, default_not_found_val=''):
        """
        :param case_sensitive:  A flag to indicate case sensitivity when matching.
        :param default_not_found_val: Default value if matching process fail.

        :return: a Dictionary with format: {field name: string extracted, ...}.
        """
        accumulator = {}  # accumulate the extracted string
        for key in self._rule:  # iterate the rule we add
            start_Fragment = self._rule[key][0]
            end_Fragment = self._rule[key][1]

            boundary_start = self.perform_matching(start_Fragment, case_sensitive).match \
                if start_Fragment is not None \
                else None
            boundary_end = self.perform_matching(end_Fragment, case_sensitive).match \
                if end_Fragment is not None \
                else None

            pattern = construct_extract_pattern(boundary_start, boundary_end)
            if pattern is None:
                accumulator[key] = default_not_found_val.__str__()
            else:
                try:
                    match = search(pattern, self._reference)
                    accumulator[key] = match.group(0) if match else default_not_found_val.__str__()
                except rer:
                    accumulator[key] = default_not_found_val.__str__()
        return accumulator


def construct_extract_pattern(start, end):
    """pattern constructor to extract text"""
    if all([start is None, end is None]):
        return None
    start = f"(?<={start})" if start is not None else ""
    end = f"(?={end})" if end is not None else ""
    return start + ".*" + end


# Since the string that we want to extract is uppercase alphabet, we define function
# to clean the extracted string
def clean_non_uppercase(string):
    """Stripe non alphabetic uppercase character that trailing the string"""
    str_length = len(string)
    start_idx = find_trailing_Uppercase_index(string, str_length)
    end_idx = find_trailing_Uppercase_index(string, str_length, -1) + 1
    end_idx = str_length if end_idx == 0 else end_idx
    return string[start_idx:end_idx]


def find_trailing_Uppercase_index(string, str_len=None, increment=1):
    """Child of clean_non_uppercase function. It iterate the index until it find
     an uppercase letter. The index will be used to slice the string."""
    str_len = len(string) if str_len is None else str_len
    start = 0 if increment == 1 else -1
    for r in range(start, str_len * increment, increment):
        if string[r] in upper:
            return r
    return 0 if increment == 1 else -1


# Now we start te preparation, lets start by defining anchor
# The word used here is Indonesian (bahasa), from left to right the field we trying
# to extract using anchor is name, sex, marital status and job.
fields_name = ["Nama", "Jenis Kelamin", "Status Perkawinan", "Pekerjaan"]
start_anchor = ["Nama :", "Jenis Kelamin :", "Status Perkawinan:", "Pekerjaan :"]
end_anchor = [None, "Gol Darah", None, None]

# Create ExtractFieldWithRegex object and start adding anchor Fragment as rule
extract = ExtractFieldWithRegex()
for i in range(len(fields_name)):
    fragments_start = Fragment(start_anchor[i])
    fragments_end = Fragment(end_anchor[i]) if end_anchor[i] is not None else None
    extract.add_rule(fields_name[i], fragments_start, fragments_end)

# Now prepare the image
path_to_images = None  # specify the path to the images
images_source_path = path_to_images
# Convert path string to Path
images_source_path = Path(images_source_path)
# Search all image path in that directory
images_path = images_source_path.glob("*.png")

# Create panda dataframe to process the extracted data
extract_accumulator = pd.DataFrame(columns=fields_name)
# Below code can be omitted.
# Setting displayed tabular data, to show our whole DataFrame
# without truncating the display.
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

count = 0
for i_path in images_path:
    count += 1
    image = open_image(str(i_path))
    # extract the image text
    reference = pytesseract.image_to_string(image, config="--oem 1 --psm 6")
    # set the reference for the extract object to match against
    extract.set_reference(reference)

    # now we perform extraction
    extracted = extract.perform_extraction()
    # create DataFrame object from the extracted result
    extracted = pd.DataFrame(extracted, index=[count])
    # merge the result with the previous one
    extract_accumulator = pd.concat([extract_accumulator, extracted])

# see the raw result
print(extract_accumulator)

# Since sex, marital status and job has a determined value, mean the result value
# can be controlled (in other word the value just a matter of multiple choice),
# we can do some matching again against a reference that we will define.

value_reference = [None,
                   ("LAKI-LAKI", "PEREMPUAN"),
                   ("KAWIN", "BELUM KAWIN", "CERAI HIDUP"),
                   ("PETANI/PEKEBUN", "BELUM/TIDAK BEKERJA", "MENGURUS RUMAH TANGGA", "WIRASWASTA",)]

# create a list to store REM object to easily iterate it when matching
match_choice = []
for ref in value_reference:
    rematch = None
    if ref is not None:
        rematch = REM()
        rematch.set_reference(ref)
    match_choice.append(rematch)

# Now we iterate it using index
for i in range(len(fields_name)):
    if match_choice[i] is not None:
        # create new list to update the value of the current result DataFrame
        new_series = []
        # now we iterate the value of a column of the DataFrame
        for value in extract_accumulator[fields_name[i]]:
            # clean non uppercase letter
            value = clean_non_uppercase(value)
            # create Fragment for the value to match it against earlier defined multiple choice
            value_Fragment = Fragment(value, 0.5)
            # now we perform matching for the value
            match = match_choice[i].perform_matching(value_Fragment)
            new_value = match.match
            # append the new value if match or the old value if not
            new_series.append(new_value) if new_value is not None else new_series.append(value)
        # here we replace the old column with new one
        extract_accumulator[fields_name[i]] = new_series

# See the end result
print('\n', extract_accumulator)

"""
As you can see, some field are missing and some aren't like what we intended it to be, 
there is many situation that could lead to this and from developer perspective 
there should be some unoptimized and miss written code somewhere.
Maybe it will be found in the future by someone and there would be and update
to this library.
"""
