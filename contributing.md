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


## Preparing a functional testing environment

Tests can be run using either a Docker container with Selenium or locally installed Selenium components.
Instructions for each procedure follow.


### Docker container with Selenium

#### Install Docker Engine

The appropriate version of Docker Engine must be installed on your system.

[Install Docker Engine](https://docs.docker.com/engine/install/) for your platform.

Additionally the user that runs the tests on your local system must have permissions to manage the docker engine to create, run, and stop docker containers.
On Windows and macOS, this is handled automatically by the installer, but Linux requires a manual step.

For Linux only, follow [Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
Optionally verify that Docker Engine is installed correctly by running the `hello-world` image.

    docker run hello-world`


#### Set environment variables

##### WEBDRIVER

The Selenium docker container can run tests using Firefox, Chrome, or Opera.
Choose the Selenium docker container on which you want to run tests.

All functional tests must pass using Firefox.
At the moment some tests fail on Chrome and Opera.
We are in process of rewriting tests to overcome the differences between browsers.
We welcome your contribution to rewriting tests in deformdemo for better compatibility across these browsers, with Chrome as a higher priority and need.

Set the `WEBDRIVER` environment variable using one of the following otpions.

    export WEBDRIVER=selenium_container_firefox
    export WEBDRIVER=selenium_container_chrome
    export WEBDRIVER=selenium_container_opera

##### URL

Set the `URL` environment variable.

    export URL=http://localhost:8522

We chose `localhost`, but you can set whatever works for your host name or IP address.

##### CONTAINERTZ

If your system's time zone is not US/Eastern, set `CONTAINERTZ` to US/Eastern.

    export CONTAINERTZ="TZ=US/Eastern"

##### WAITTOSTART

By default, tests will wait up to 30 seconds for the Selenium Docker container to be pulled and started.
If your machine needs more time to start up, you can increase the wait time by setting the `WAITTOSTART` environment variable.

    export WAITTOSTART=60

##### *DOCKERVERSION

Currently the Selenium Docker container version with the latest tag will be pulled from Docker Hub.
This can be changed by setting one of the following appropriate environment variables.

    export FIREFOXDOCKERVERSION="selenium/standalone-firefox:4.0.0-alpha-7-prerelease-20200826"`
    export CHROMEDOCKERVERSION="selenium/standalone-chrome:4.0.0-alpha-7-prerelease-20200826"
    export OPERADOCKERVERSION="selenium/standalone-opera:4.0.0-alpha-7-prerelease-20200826"

You can get a [specific Selenium docker container release](https://github.com/SeleniumHQ/docker-selenium/releases).

Now the environment is ready to run tox.


### Locally installed Selenium components

To avoid conflicts with other possibly installed versions of applications, we suggest that you install the following applications into your local checkout of Deform.
We will assume that you put your projects in your user directory, although you can put them anywhere.

    cd ~/projects/deform/


#### Add your checkout location to your `$PATH`

You must add your local Deform checkout—which is also where you will install your web driver and web browser—to your `$PATH` to run tox or nosetests.
Otherwise Firefox or Chrome will not start and will return an error message such as `'geckodriver' executable needs to be in PATH.`.

When you run `$tox -e functional3`, your local checkout is automatically added to your `$PATH`.
Otherwise you can set it manually. 

    export PATH=~/projects/deform:$PATH


#### Set `WEBDRIVER` environment variable

To use a locally installed web driver and web browser, you must set the `WEBDRIVER` environment variable.
Choose the browser in which you want to run tests with one of the following command options.

    export WEBDRIVER=selenium_local_firefox
    export WEBDRIVER=selenium_local_chrome

All functional tests must pass using Firefox.
At the moment some tests fail on Chrome and Opera.
We are in process of rewriting tests to overcome the differences between browsers.
We welcome your contribution to rewriting tests in deformdemo for better compatibility across these browsers, with Chrome as a higher priority and need.


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
    wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-macos.tar.gz
    tar -xzf geckodriver-v0.27.0-macos.tar.gz

    # Linux
    wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
    tar -xzf geckodriver-v0.27.0-linux64.tar.gz

On macOS you need to issue a command to remove the webdriver from quarantine whenever you install a new version.

    xattr -r -d com.apple.quarantine geckodriver

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


### Testing on Chrome

You can also run tests on Chrome.
Tests might not run correctly on Chrome due to various timing issues.
Pull requests with corrected functional tests are welcome!

Installation and configuration is similar to Firefox, with the following differences.

#### Chrome latest

##### macOS

[Download the latest version of Chrome for your platform](https://www.google.com/chrome/).

Open the `.dmg` (macOS), and drag the Chrome icon to:

    ~/projects/deform/

#### chromedriver

Install the [latest release of chromiumdriver](https://chromedriver.chromium.org/downloads).

Unzip the archive, and move the chromedriver icon to:

    ~/projects/deform/

On macOS you might need to issue a command to remove the webdriver from quarantine whenever you install a new version.

    xattr -r -d com.apple.quarantine chromedriver

#### Set an environment variable for `WEBDRIVER`

In `deformdemo/test.py`, the `setUpModule` reads an environment variable to determine which webdriver to run.

    export WEBDRIVER=chrome
