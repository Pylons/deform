# Contributing

You are working on the `main` branch. Development of new features takes place on the `main` branch. The latest, stable release branch is `2.0-branch`.

All projects under the Pylons Projects, including this one, follow the guidelines established at [How to Contribute](https://pylonsproject.org/community-how-to-contribute.html), [Coding Style and Standards](https://pylonsproject.org/community-coding-style-standards.html), and [Pylons Project Documentation Style Guide](https://docs.pylonsproject.org/projects/docs-style-guide/).

You can contribute to this project in several ways.

* [File an Issue on GitHub](https://github.com/Pylons/deform/issues).
* Fork this project and create a branch with your suggested change. When ready, submit a pull request for consideration. [GitHub Flow](https://guides.github.com/introduction/flow/index.html) describes the workflow process and why it's a good practice. When submitting a pull request, sign [CONTRIBUTORS.txt](https://github.com/Pylons/deform/blob/main/CONTRIBUTORS.txt) if you have not yet done so. Also update [CHANGES.txt](https://github.com/Pylons/deform/blob/main/CHANGES.txt) with a change log entry.
* Join the [IRC channel #pyramid on irc.freenode.net](https://webchat.freenode.net/?channels=pyramid).
* Join the [Pylons team on Keybase](https://keybase.io/team/pylons).


## Discuss proposed changes first

To propose a change, open an issue on GitHub for discussion, preferably before starting any coding.
Ask the maintainers' opinions for how the issue should be approached, as this will make it easier to merge the pull request later.


## Documentation

All features must be documented with code samples in narrative documentation, API documentation, and in [deformdemo](https://github.com/Pylons/deformdemo).


## Setting up a development environment

For ease of documentation, we assume that you will clone Deform to `~/projects/deform` and do all your work within that directory.
Adjust commands according to your custom locations.

Clone the Deform repository.

    git clone https://github.com/Pylons/deform.git ~/projects/deform

Set an environment variable to your virtual environment.

    export VENV=~/projects/deform/env

Create a virtual environment using Python's [venv](https://docs.python.org/3/library/venv.html) module.

    cd ~/projects/deform
    python3 -m venv $VENV

Into this virtual environment, install Deform development requirements for unit testing, lint, docs, and functional testing with the command

    $VENV/bin/pip install -e ".[dev]"

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

    $VENV/bin/pip3 install --user tox
    export TOX=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')/tox

See `tox.ini` at the root of the repository for currently supported environments.

We recommend that you install all supported Pythons, prepare a functional testing environment (see [Preparing a functional testing environment](#preparing-a-functional-testing-environment) below), and run the full test suite using tox before submitting a pull request.
If you are unable to do so, GitHub will run the full test suite across supported environments for you when you open a pull request.
Pull requests must pass all tests and tox environments before they can be merged.

After you have set up your development environment, you can use tox to run a specific environment by specifying it on the command line, or multiple environments as comma-separated values.

    $TOX -e py39,docs


## Coding Style

Deform uses [Black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/) for code formatting style.
To run formatters:

    $TOX -e format


## Unit tests

All features must be covered by unit tests, so that test coverage stays at 100%.


## Functional tests

All features must be covered by functional tests and have example usage.
We use the following for running functional tests.

* A web browser's latest version.  We require Firefox for tests, and Chrome or Opera are optional.
* A Selenium web driver to go with the web browser.
* [Selenium 3.x](https://pypi.org/project/selenium/)
* [gettext](https://www.gnu.org/software/gettext/)
* [tox](https://tox.readthedocs.io/en/latest/)
* [deformdemo](https://github.com/pylons/deformdemo)


### Running functional tests

See [Preparing a functional testing environment](#preparing-a-functional-testing-environment) before trying to run functional tests.

For functional tests, `tox` runs the shell script [run-selenium-tests.bash](https://github.com/Pylons/deform/blob/main/run-selenium-tests.bash), located at the root of the Deform repository.
See its comments for a description.

To run functional tests.

    $TOX -e functional3

Stop on error.

    $TOX -e functional3 -- -x

Run only the last failed tests.

    $TOX -e functional3 -- --lf

Run a single test class.

    $TOX -e functional3 -- deformdemo/test.py::CheckedInputWidgetWithMaskTests

Run a single test method in a class.

    $TOX -e functional3 -- deformdemo/test.py::SequenceOfMaskedTextInputs::test_submit_one_filled


### When to add or edit functional tests

If you add a feature to Deform, or change a feature in Deform that causes any functional test to fail, then you also must add sufficient functional tests to the [deformdemo](https://github.com/pylons/deformdemo) repository.
The following is the recommended procedure.
If you have any trouble, please ask for assistance via the [issue tracker](https://github.com/pylons/deform/issues/).

1.  Follow the instructions under [Preparing a functional testing environment](#preparing-a-functional-testing-environment) below.

2.  Run `$TOX` in Deform.
    We run tox to establish that code is linted and passing tests before you change anything.
    This will run all environments defined in `tox.ini`.
    It is OK if you do not have all supported Python versions installed.
    One of those environments will run a script that clones deformdemo into a  directory `deformdemo_functional_tests` inside your Deform checkout, then runs functional tests.

3.  Run `$TOX` in deformdemo.
    Change your working directory to `deformdemo_functional_tests` and run tox to make sure functional tests pass in deformdemo as well.

        cd deformdemo_functional_tests
        $TOX

4.  Configure git remote repositories.
    Set `origin` to your remote fork, and set `upstream` to point to `Pylons` for both Deform and deformdemo.
    You need to `cd` into each directory, `deformdemo_functional_tests` and `Deform`, and execute the following commands.
    
        cd deform
        git remote add upstream https://github.com/Pylons/deform.git
        git remote set-url origin git@github.com:git_user_id/deform.git
        
        cd deformdemo_functional_tests
        git remote add upstream https://github.com/Pylons/deformdemo.git
        git remote set-url origin git@github.com:git_user_id/deformdemo.git

5.  Create a new branch on both Deform or Deformdemo with the same name.

6.  Update your code, and run `$TOX` again locally, both in Deform and deformdemo as in Steps 2 and 3, making sure all tests pass.

7.  Only after you complete the previous step, then submit a pull request to both repositories for review.

All pull requests automatically run all tests across all tox environments.
However when there are paired pull requests in both Deform and deformdemo, we have a chicken-and-egg situation.
Each repository cannot pull the version of the other referenced in the pull request to run functional tests.
Automated testing will fail for both pull requests.

The maintainers of both projects work around this as follows.

1.  In Travis, ensure that all of Deform's automated builds pass, except for the functional test build, for that pull request.
2.  Checkout both branches in the paired pull requests, and run tox locally to ensure all builds pass.
3.  Merge the pull request.
4.  Now deformdemo can pull the desired version of Deform. Restart the failing jobs for deformdemo to ensure that functional tests pass.
5.  When all automated builds tests pass, then merge the pull request in deformdemo.


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

    docker run hello-world


#### Set environment variables

##### WEBDRIVER

The Selenium docker container can run tests using Firefox, Chrome, or Opera.
Choose the Selenium docker container on which you want to run tests.

All functional tests must pass using Firefox.
At the moment some tests fail on Chrome and Opera.
We are in process of rewriting tests to overcome the differences between browsers.
We welcome your contribution to rewriting tests in deformdemo for better compatibility across these browsers, with Chrome as a higher priority and need.

Set the `WEBDRIVER` environment variable using one of the following options.

    export WEBDRIVER=selenium_container_firefox
    export WEBDRIVER=selenium_container_chrome
    export WEBDRIVER=selenium_container_opera

##### URL

Set the `URL` environment variable.

    export URL=http://<lan_ip_address>:8523

If you do not know your LAN IP address, try the command:

    ipconfig getifaddr en0

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


#### Set `WEBDRIVER` environment variable

To use a locally installed web driver and web browser, you must set the `WEBDRIVER` environment variable.
This is read by `deformdemo/test.py` when running the functional tests.
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
    wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-macos.tar.gz
    tar -xzf geckodriver-v0.31.0-macos.tar.gz

    # Linux
    wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
    tar -xzf geckodriver-v0.31.0-linux64.tar.gz

On macOS you need to issue a command to remove the webdriver from quarantine whenever you install a new version.

    xattr -r -d com.apple.quarantine geckodriver

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
