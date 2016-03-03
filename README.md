<p align="center">
  <img src="https://avatars0.githubusercontent.com/u/1316274?v=3&s=200">
</p>

TML Library For Python
==================
[![Build Status](https://travis-ci.org/translationexchange/tml-python.png?branch=master)](https://travis-ci.org/translationexchange/tml-python)
[![Coverage Status](https://coveralls.io/repos/translationexchange/tml-python/badge.png?branch=master)](https://coveralls.io/r/translationexchange/tml-python?branch=master)
[![Dependency Status](https://www.versioneye.com/user/projects/54c1457a6c00352081000416/badge.svg?style=flat)](https://www.versioneye.com/user/projects/54c1457a6c00352081000416)

TML library for Python is a set of classes that provide translation functionality for any Python based application.
The library uses Translation Markup Language that allows you to encode complex language structures in simple, yet powerful forms.

The library works in conjunctions with TranslationExchange.com service that provides machine and human translations for your application.
In order to use the library, you should sign up at TranslationExchange.com, create a new application and copy the application key and secret.


Django Integration
==================

If you are planning on using TML in a Django application, you should use tml-python-django package.

https://github.com/translationexchange/tml-python-django


Installation
==================

To install the package, use pip:

```ssh
pip install tml
```


Registering Your App
===================================

Before you can proceed with the integration, please register with http://translationexchange.com and create a new application.

At the end of the registration process you will be given a key and a secret. You will need to enter them in the initialization function of the TML SDK.



Usage
==================

The library can be invoked from the IRB. To use TML client you must require it, and instantiate the application with the key and secret of your app from translationexchange.com:

```python
>>> import tml
>>> ...
```

Now you can use the application to get any language registered with your app:

```python
>>> ...
```

Simple example:

```python
>>> ...
```

Using description context:

```python
>>> ...
```

Numeric rules with piped tokens:

```python
>>> ...
```

Gender rules:

```python
>>> ...

>>> ...
```

Gender rules with language cases:

```python
...
```

Decoration tokens:

```python
...
```

Nested decoration tokens:

```python
...
```

Data tokens with decoration tokens together:

```python
...
```

PS. The Russian translation on translationexchange.com could either be provided by a set of 6-9 simple translations for {genders}(male, female, unknown) * count{one, few, many} or by a single advanced translation
in the form of:

```python
...
```

Or in a simpler form:

```python
...
```

One of the advantages of using TML is the ability to easily switch token values. The above example in a text based email can reuse translations:

```python
...
```

You should also notice that all of the translation keys you've been using in your experiments will be registered under your application by the translationexchange.com service. You can view them all at:

https://dashboard.translationexchange.com/

If any translation key you've tried to translate was missing a translation, you can manually translate it using the service (with the help of a machine translation suggestion).

```python
...
```

Then without leaving your IRB session, you can call the following method to reset your application cache:

```python
...
```

Then you can just rerun the translation method with the missing translation and you should get back the translated value.

```python
...
```

Links
==================

* Register on TranslationExchange.com: http://translationexchange.com

* Read TranslationExchange's documentation: http://docs.translationexchange.com

* Follow TranslationExchange on Twitter: https://twitter.com/translationx

* Connect with TranslationExchange on Facebook: https://www.facebook.com/translationexchange

* If you have any questions or suggestions, contact us: feedback@translationexchange.com


Copyright and license
==================

Copyright (c) 2016 Translation Exchange, Inc

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.