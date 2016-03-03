<p align="center">
  <img src="https://avatars0.githubusercontent.com/u/1316274?v=3&s=200">
</p>

TML For Python
==================

TML for Python is a set of classes that provide translation functionality for any Python based application.

The library works in conjunctions with translationexchange.com service that provides machine and human translations for your application.
In order to use the library, please sign up at translationexchange.com, create a new application and copy the application token.


Django Integration
==================

To be done

Installation
==================

To install using pip, use:

pip install tml


Registering Your App
===================================

Before you can proceed with the integration, please register with https://translationexchange.com and create a new application.

At the end of the registration process you will be given a key and a secret. You will need to enter them in the initialization function of the Tr8n SDK.



Usage
==================

The library can be invoked from the python command. To use client you must require it, and instantiate the application with the key and secret of your app from tr8nhub.com:

Code Coverage
=============

* Install coverage package with `pip install -r requires_dev.txt`

* Execute `nosetests tests/unit/* --all --verbose --with-coverage --cover-package=tml`

* Enjoy the numbers


Debugging
---------
---------
curl -F "access_token=<access-token>" -F "source_keys=<url-encoded-payload>" "https://staging-api.translationexchange.com/v1/sources/register_keys"


Links
==================

* Register on TranslationExchange.com: http://translationexchange.com

* Read Translation Exchange documentation: http://translationexchange.com/docs

* Follow TranslationExchange on Twitter: https://twitter.com/translationx

* Connect with TranslationExchange on Facebook: https://www.facebook.com/translationexchange

* If you have any questions or suggestions, contact us: feedback@translationexchange.com


Copyright and license
=====================

Copyright (c) 2015 Translation Exchange Inc

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
