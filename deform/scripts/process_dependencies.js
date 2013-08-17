#!/bin/sh
':' //; exec "`command -v nodejs || command -v node`" "$0"

// You can run this file in the following ways:
// 1. execute the file from the console
// 2. "npm run-script process-dependencies"

var bower = require('bower');
var fs = require('fs');
var path = require('path');
var _ = require('lodash');
var q = require('q');

function basename(file) {
    return file.replace(/\\/g,'/').replace( /.*\//, '' );
}

function dirname(file) {
    return file.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
}

function processDependencies(pkg) {
    // take main of this package
    var result = pkg.pkgMeta.main || [];
    if (typeof result == 'string') {
        // if main was a string instead of a list
        result = [result];
    }
    var folder = pkg.canonicalDir;
    result = _.map(result, function(file) {
        return path.join(folder, file);
    });
    // store it also on result, for a 2nd pass processing
    pkg._depResult = result;
    // add other dependencies
    _.forEach(pkg.dependencies, function(depPkg) {
        var depDeps = processDependencies(depPkg);
        result = _.union(depDeps, result);
    });
    return result;
}

// 2nd pass uses depResult
function processMap(pkg, basePath) {
    var depResult = pkg._depResult;
    var pkgInfo = {
        name: pkg.pkgMeta.name,
        version: pkg.pkgMeta.version
    }
    pkgInfo.js = _.map(
        _.filter(depResult, function(elem) {
            return /.js$/.test(elem.toLowerCase());
        }), function(elem) {
            return path.join(basePath, 'js', basename(elem));
        }
    );
    pkgInfo.css = _.map(
        _.filter(depResult, function(elem) {
            return /.css$/.test(elem.toLowerCase());
        }), function(elem) {
            return path.join(basePath, 'css', basename(elem));
        }
    );
    pkgInfo.dependencies = [];
    // add other dependencies
    _.forEach(pkg.dependencies, function(depPkg) {
        var depMap = processMap(depPkg, basePath);
        pkgInfo.dependencies.push(depMap);
    });
    return pkgInfo;
}


function main() {

    function getBowerListing() {
        // do a 'bower list'
        var d = q.defer();
        bower.commands
        .list({})
        .on('end', function (result) {
            console.log('"bower list" finished.');
            d.resolve(result);
        }).on('error', function (error) {
            d.reject('Bower error: ' + error);
        });
        return d.promise;
    }

    function processListing(result) {
        // where files go, relative from cd
        var outputDir = 'deform/static/dist';
        // path of the files starting from static (will be part of the output)
        var basePath = 'dist';

        // get the dependencies
        var deps = processDependencies(result);
        var map = processMap(result, basePath);
        var outputFilename = path.join(outputDir, 'map.json');
        var formatted = JSON.stringify(map, null, 4);

        function saveMap() {
            var d = q.defer();
            fs.writeFile(outputFilename, formatted, function(err) {
                if (err) {
                    d.reject('File write error: ' + err);
                } else {
                    console.log("JSON saved to " + outputFilename);
                    d.resolve();
                }
            });
            return d.promise;
        }

        function copyAllFiles() {
            // separate js and css
            var jsDeps = _.filter(deps, function(elem) {
                return /.js$/.test(elem.toLowerCase());
            });
            var cssDeps = _.filter(deps, function(elem) {
                return /.css$/.test(elem.toLowerCase());
            });

            function makeDir(dir) {
                return function() {
                    var d = q.defer();
                    var dirName = path.join(outputDir, dir);
                    fs.mkdir(dirName, function(err) {
                        if (! err) {
                            console.log('Created directory "' + dirName + '"');
                        }
                        if (! err || (err && err.code === 'EEXIST')) {
                            d.resolve();
                        } else {
                            d.reject('Directory creation of " + dir + " failed: ' + err);
                        }
                    });
                    return d.promise;
                };
            }

            function copy(type, deps) {
                return function() {
                    // Copy the files.
                    function copyOne(fname) {
                        var d = q.defer();
                        var dest = path.join(outputDir, type, basename(fname));
                        var rd = fs.createReadStream(fname);
                        rd.on("error", function(err) {
                            d.reject('File error: ' + err);
                        });
                        var wr = fs.createWriteStream(dest);
                        wr.on("error", function(err) {
                            d.reject('File error: ' + err);
                        });
                        wr.on("close", function(ex) {
                            console.log('Copied "' + fname + '" to "' + outputDir + '"');
                            d.resolve();
                        });
                        rd.pipe(wr);
                        return d.promise;
                    }
                    return q.all(_.map(deps, copyOne));
                };
            }

            return q.all([
                makeDir('js')().then(copy('js', jsDeps)),
                makeDir('css')().then(copy('css', cssDeps))
            ]);
        }

        return q.all([saveMap(), copyAllFiles()]);
    }

    return getBowerListing().then(processListing);
}


main().then(function() {
    console.log('OK, all went good.');
    process.exit(0);
}, function(error) {
    console.log('Error: ' + error);
    process.exit(1);
});
