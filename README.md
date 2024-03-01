# Python Bootstring

This is a Python implementation of the Bootstring encoding algorithm,
as described in [RFC 3492](https://tools.ietf.org/html/rfc3492).

The Bootstring encoding algorithm is used to encode Unicode strings
into ASCII strings, and is used by the Punycode encoding algorithm.

This implementation passes all the tests in the RFC 3492 test suite,
however is is not optimized for performance and might fail on edge cases
not covered by the test suite.

To use it, simply `pip install git+https://github.com/frereit/bootstring/` and `import bootstring`:

```python
>>> import bootstring
>>> bootstring.encode("hello, world!")
'hello, world!-'
>>> bootstring.decode("hello, world!-")
'hello, world!'
>>> bootstring.encode("döner")
'dner-5qa'
>>> bootstring.decode("dner-5qa")
'döner'
>>> bootstring.encode("他们为什么不说中文")
'ihqwcrb4cv8a8dqg056pqjye'
>>> bootstring.decode("ihqwcrb4cv8a8dqg056pqjye")
'他们为什么不说中文'
```