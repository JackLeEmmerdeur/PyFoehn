from os.path import isfile  # , expanduser as opexpanduser, join as opjoin, dirname as opdirname
from six import string_types, text_type
from re import findall
from sys import exc_info
from traceback import format_exception


def is_string(var):
	return isinstance(var, string_types)


def is_integer(var):
	return isinstance(var, int)


def is_boolean(var):
	return isinstance(var, bool)


def is_unicode(obj):
	return isinstance(obj, text_type)


def parse_sequence_str(seqstr):
	list(map(lambda x: int(x), findall('\d+', seqstr)))


def is_sequence(var):
	"""
	Tests if var is a sequenzish instance (list or tuple)
	:param var: The possible sequence instance
	:return: True if var is a sequence instance
	"""
	return (
			not hasattr(var, "strip") and
			hasattr(var, "__getitem__") or
			hasattr(var, "__iter__")
	)


def is_dict(var):
	return isinstance(var, dict)


def file_exists(fileobj):
	"""
	Checks file existance
	:param fileobj: Can be a string (path), file-descriptor (int)
	:return: True or False
	"""
	if isinstance(fileobj, string_types) or isinstance(fileobj, text_type) or isinstance(fileobj, int):
		return isfile(fileobj)
	else:
		return False


def string_is_empty(
		thetext,
		preserve_whitespace=False,
		check_strip_availability=False
):
	"""
	Checks if `thetext` is emtpy and returns True if so.

	Example:
	>>> string_is_empty("  ")
	True
	>>> string_is_empty("  ", True)
	False
	>>> string_is_empty("  ", False)
	True

	:param thetext: The string to check for emptiness
	:param preserve_whitespace: If True, blankspaces will not count as empty
	:param check_strip_availability: Checks if `thetext is a string-type via availability of strip-method (esotheric)
	:return: True if `thetext` is empty
	:rtype: bool
	"""
	if thetext is None:
		return True
	isstring = False
	if check_strip_availability:
		isstring = hasattr(thetext, "strip")
	elif is_string(thetext) or is_unicode(thetext):
		isstring = True
	if isstring or isinstance(thetext, bytes):
		return len(thetext if preserve_whitespace else thetext.strip()) < 1
	else:
		return True


def get_reformatted_exception(msg, e):
	tb = ""
	excfmtlist = format_exception(type(e), e, exc_info()[2])
	for (index, excfmtitem) in enumerate(excfmtlist):
		if index > 0:
			tb += "\r\n"
		tb += "\t" + excfmtitem
	return "{}\r\n{}".format(msg, tb)


def file_exists(path):
	return isfile(path)
