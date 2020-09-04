# Contributing

You are working on the `master` branch. Development of new features takes place on the `master` branch. The latest, stable release branch is `2.0-branch`.

All projects under the Pylons Projects, including this one, follow the guidelines established at [How to Contribute](https://pylonsproject.org/community-how-to-contribute.html), [Coding Style and Standards](https://pylonsproject.org/community-coding-style-standards.html), and [Pylons Project Documentation Style Guide](https://docs.pylonsproject.org/projects/docs-style-guide/).

You can contribute to this project in several ways.

* [File an Issue on GitHub](https://github.com/Pylons/deform/issues)
* Fork this project and create a branch with your suggested change. When ready, submit a pull request for consideration. [GitHub Flow](https://guides.github.com/introduction/flow/index.html) describes the workflow process and why it's a good practice. When submitting a pull request, sign [CONTRIBUTORS.txt](https://github.com/Pylons/deform/blob/master/CONTRIBUTORS.txt) if you have not yet done so. Also update [CHANGES.txt](https://github.com/Pylons/deform/blob/master/CHANGES.txt) with a change log entry.
* Join the [IRC channel #pyramid on irc.freenode.net](https://webchat.freenode.net/?channels=pyramid).


## Discuss proposed changes first

To propose a change, open an issue on GitHub for discussion, preferably before starting any coding.
Ask the authors' opinion how the issue should be approached, as this will make it easier to merge the pull request later.


## Documentation

All features must be documented with code samples in narrative documentation, API documentation, and in [deformdemo](https://github.com/Pylons/deformdemo).


## Setting up a development environment

Create a virtual environment using Python's [venv](https://docs.python.org/3/library/venv.html) module.

    python3 -m venv /path/to/new/virtual/environment

Activate newly installed virtual environment.

    /path/to/new/virtual/environment/bin/activate

Into this virtual environment, install Deform development requirements for unit testing, lint, docs, and functional testing with the command

    pip install -e ".[dev]"

Continue by installing tox and following [Preparing a functional testing environment](#preparing-a-functional-testing-environment) below.


## Using tox

We use [tox](https://tox.readthedocs.io/en/latest/install.html) to:

- manage virtual environments
- run both unit and functional tests across all supported versions of Python
- build docs
- perform lint checks
- perform test coverage
- format code

Install `tox` either in your path or locally.
The examples below assume that `tox` was installed with:

    pip3 install --user tox
    export TOX=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')/tox

See `tox.ini` at the root of the repository for currently supported environments.

We recommend that you install all supported Pythons, prepare a functional testing environment (see [Preparing a functional testing environment](#preparing-a-functional-testing-environment) below), and run the full test suite using tox before submitting a pull request.
If you are unable to do so, GitHub will run the full test suite across supported environments for you when you open a pull request.
Pull requests must pass all tests and tox environments before they can be merged.

After you have set up your development environment, you can use tox to run a specific environment by specifying it on the command line, or multiple environments as comma-separated values.

    $TOX -e py38,docs


## Coding Style

Deform uses [Black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/) for code formatting style.
To run formatters:

    $TOX -e format


## Unit tests

All features must be covered by unit tests, so that test coverage stays at 100%.


## Functional tests

All features must be covered by functional tests and have example usage.
We use the following for running functional tests.

* Firefox latest
* geckodriver
* [Selenium 3.x](https://pypi.org/project/selenium/)
* [gettext](https://www.gnu.org/software/gettext/)
* [tox](https://tox.readthedocs.io/en/latest/)
* [deformdemo](https://github.com/pylons/deformdemo)

If you add or change a feature that reduces test coverage or causes a functional test to fail, then you also must submit a pull request to the [deformdemo](https://github.com/pylons/deformdemo) repository to go along with your functional test change to Deform.

For functional tests, `tox` runs the shell script [run-selenium-tests.bash](https://github.com/Pylons/deform/blob/master/run-selenium-tests.bash), located at the root of the Deform repository.
See its comments for a description.

To run functional tests.

    $TOX -e functional3

Stop on error.

    $TOX -e functional3 -- -x

Run only the last failed tests.

    $TOX -e functional3 -- --failed

Run a single test.

    $TOX -e functional3 -- deformdemo.test:CheckedInputWidgetWithMaskTests

    $TOX -e functional3 -- deformdemo.test:SequenceOfMaskedTextInputs.test_submit_one_filled


### Preparing a functional testing environment

Tests can be run against Selenium docker container or against locally installed driver.

## Selenium Container based driver and browser

Docker Engine must be installed on the system and the user that run the tests on local system must have proper access to manage the docker engine to create, run and stop docker container.
 
follow [installation instruction](https://docs.docker.com/engine/install/), and then follow [post installation](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) then verify that Docker Engine is installed correctly by running the hello-world image.
`docker run hello-world`


Setting one of the following environment variables are madatory to choose which Selenium docker container tests are going to run against:

Firefox is the main stream which must pass all the tests, but at the moment some tests are failing on Chrome or Opera and we are in process of rewritting tests to overcome the differences in these browsers. you are more than welcome to contribue in rewriting tests in Deformdemo.

`export WEBDRIVER=selenium_container_chrome`
`export WEBDRIVER=selenium_container_opera`
`export WEBDRIVER=selenium_container_firefox`

Setting URL environment varaible is mandatory:

`export URL=http://host_name_or_host_ip_address:8522`

Please note localhost and 127.0.0.1 won't work, it has to be either host name or host ip address.

If the system time zone is not US/Eastern please set CONTAINERTZ to host time zone.
`export CONTAINERTZ="TZ=US/Eastern"`

Currently tests will wait 30 seconds for Selenium docker container to be pulled and started, if local host slow and needs more time to start up the container then increase the time by setting the WAITTOSTART environment variable.
`export WAITTOSTART=60`

Currently Selenium docker container version with latest tag will be pulled from docker hub, but this can be changed by setting either of following environment variables.

`export OPERADOCKERVERSION="selenium/standalone-opera:4.0.0-alpha-7-prerelease-20200826"`
`export CHROMEDOCKERVERSION="selenium/standalone-chrome:4.0.0-alpha-7-prerelease-20200826"`
`export FIREFOXDOCKERVERSION="selenium/standalone-firefox:4.0.0-alpha-7-prerelease-20200826"`

Selenium docker container release can be found here.

https://github.com/SeleniumHQ/docker-selenium/releases

At this point environment is ready to run tox.



## Local driver and local browser


To use locally installed driver and browser one of the following environment variables needs to be set:
export WEBDRIVER=selenium_local_chrome
export WEBDRIVER=selenium_local_firefox

Again, Firefox is main stream, and all functional tests shall pass against Firefox.


To avoid conflicts with other possibly installed versions of applications, we suggest that you install the following applications into your local checkout of Deform.
We will assume that you put your projects in your user directory, although you can put them anywhere.

    cd ~/projects/deform/


#### Add your checkout location to your `PATH`

You must add your local Deform checkout—which is also where you will install geckodriver and your web browser—to your `PATH` to run `tox` or nosetests
Otherwise Firefox or Chrome will not start and will return an error message of `'geckodriver' executable needs to be in PATH.`.

When you run `$tox -e functional3`, your local checkout is automatically added.
Otherwise you can set it manually. 

    export PATH=~/projects/deform:$PATH


#### Firefox latest

##### macOS

[Download the latest version of Firefox for your platform](https://www.mozilla.org/en-US/firefox/all/).

Open the `.dmg` (macOS), and drag the Firefox icon to:

    ~/projects/deform/

##### Linux (Debian)

Use cURL or wget.
See the [Firefox download README.txt](https://ftp.mozilla.org/pub/firefox/releases/latest/README.txt) for instructions.
For example on Linux:

    cd ~/projects/deform/
    wget -O firefox-latest.tar.bz2 \
    "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"

Decompress the downloaded file.

    tar -xjf firefox-latest.tar.bz2


#### geckodriver

Install the [latest release of geckodriver](https://github.com/mozilla/geckodriver/releases).

    # macOS
    wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-macos.tar.gz
    tar -xzf geckodriver-v0.26.0-macos.tar.gz

    # Linux
    wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
    tar -xzf geckodriver-v0.26.0-linux64.tar.gz


#### gettext

The functional tests require the installation of the GNU `gettext` utilities, specifically `msgmerge` and `msgfmt`.
Use your package manager to install these requirements.

##### macOS
 
Use [Homebrew](https://brew.sh/):

    brew install gettext
    brew link gettext --force

If you ever have problems building packages, you can always unlink it.

    brew unlink gettext

##### Linux (Debian)

    apt-get install gettext
    apt-get install gettext-base

##### Linux (Fedora)

    dnf install gettext


#### Selenium

Selenium is installed automatically by tox via `pip install -e ".[dev]"`.


### Testing on Chrome or Chromium

Tests might not run correctly on Chrome due to various timing issues.
Some effort was put forth to fix this many years ago, but it was a never ending swamp.
However, [the situation might have improved recently](https://developers.google.com/web/updates/2017/04/headless-chrome).

If you accept the challenge, we welcome pull requests to this contributing guide, along with tests to support testing on Chrome.
The following are some clues to get you started.

- To use google-chrome or Chromium, download the web browser and respective webdriver, [chromiumdriver](https://chromedriver.chromium.org/downloads).
  These would be used instead of Firefox and geckodriver.
- Set the `WEBDRIVER` environment variable to chromiumdriver instead of geckodriver.
- Profit! Fun! World domination!
