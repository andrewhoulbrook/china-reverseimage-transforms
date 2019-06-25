# China Reverse Image Search (Maltego Transforms)

A set of three Maltego local transforms useful for performing reverse image searches via three of the most popular search engines in mainland China. 

<center>

![Baidu Images](/doc/baidu.jpg)            | ![Qihoo 360 Images](/doc/so360.jpg)       | ![Sogou Images](/doc/sogou.jpg)           |  
:-----------------------------------------:|:-----------------------------------------:|:-----------------------------------------:|
[Baidu Images](https://images.baidu.com/)  | [Qihoo 360 Images](http://images.so.com/) | [Sogou Images](https://image.sogou.com/)  |

</center>

These transform scripts are old but have been recently modified and remain useful at the time of writing.  

## Getting Started

Reverse image searching is an often used technique among OSINT practitioners and during digital forensic investigations. From detecting fake online profiles and uncovering social media footprints to brand monitoring and geolocation, reverse image searching has many uses.  

Common tools include [Google Images](http://images.google.com), [Tineye](https://www.tineye.com), [Yandex Images](https://yandex.ru/images/) and [RootAround](http://rootabout.com/) to name a few. Find more at ['OSINT Framework.com'](https://osintframework.com/). 

In China, Baidu is the king of search. Baidu also has a powerful reverse image search facility but one that I feel has become significantly less accurate and useful over time. For reverse image searching needs at least, I also find it useful to try some of the other larger Chinese search engines; they often return useful results in addition to those found via Baidu. 

These scripts aim to help quickly push reverse image queries, within Maltego, across the three best reverse image search engines in China and combine their results.  

<center>

Baidu Reverse Image Search                        |
:------------------------------------------------:|
![Baidu - Jack Ma Test Image](/doc/jack_baidu.png)|

Qihoo 360 Reverse Image Search                    |
:------------------------------------------------:|
![360 - Jack Ma Test Image](/doc/jack_360.png)    |

</center>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The transforms are written in Python 2.7.

They require Selenium and the [PhantomJS](http://phantomjs.org/) headerless Webdriver, or something else like [Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/), installed locally.  

You'll need the following Python modules installed if you don't already have them:

```
import requests
from selenium import webdriver
from fake_useragent import UserAgent
```
and

```
import MaltegoTransform
```

This last module import is the Maltego python transform library. You can grab a copy from the [Maltego developer site](https://docs.maltego.com/helpdesk/attachments/2015007304961). 

### Installing

Make sure to set the correct path to your Webdriver in each of the three scripts.

All modules used in the scripts are available from PyPI and can easily be installed as follows:

```
pip install requests, beautifulsoup4, selenium
pip install fake-useragent
```

The scripts require some improvement and can be written more efficiently. They currently make use of a mixture of Selenium and the Requests library. 

Configure the local transforms in Maltego, [see the Configuration Guide](https://docs.maltego.com/support/solutions/articles/15000010781-local-transforms). In short, you'll need to link the transforms to specific entity types and point Maltego to your local Python installation and your local copy of these transform scripts. 

I kept it simple and linked my transforms to operate off the ```maltego.image``` entity which is a standard built-in entity type. 

## Running the Transforms

These transforms can be run like any other local transforms. I find it useful to add all three into a Maltego **Transform Set**, making it easier to group and locate them all in one place on Maltego menus. This also allows me to easily run a query across all three reverse image search engines with a single click.  

<p align="center">
  <img src="/doc/news_image1.gif"/>
</p>

The tranforms return the reverse image search results as ```maltego.website``` entities to the chart. Each results entity has a small amount of meta-data fields associated with it such as the source URL, image URL and the search engine returning the results.

<p align="center">
  <img src="/doc/news_image2.gif"/>
</p>

For Sogou and Qihoo 360, the search results are categorized as either **exact matching images** or **visually similar images**. A field within the Maltego entity added to the chart will also indicate whether the image was found as the result of an exact or visually similar match. Search results featuring exact matches to the reference image will also be highlighted on the chart using a **red** coloured link and a red Maltego entity **Bookmark**, making it easier to select a subset of only exact matches within the results returned to the chart. 

The Sogou and Qihoo 360 scripts could be split into two different levels of transforms if desired: one to return exact matches only; the other to return visually similar matching images.  

The scripts are rudimentary and only scrape the first page of results for each of the three Chinese search engines.  

## Built With

* [Python](http://www.python.org)
* [Selenium](https://www.seleniumhq.org/)
* [PhantomJS](http://phantomjs.org/)
* [Maltego Local Python Library](https://docs.maltego.com/support/solutions/articles/15000019558-python-local-library-reference)

## Authors

* **Andrew Houlbrook** - *Initial work* - [andrewhoulbrook](https://github.com/andrewhoulbrook)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details