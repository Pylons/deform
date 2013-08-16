#!/bin/sh
':' //; exec "`command -v nodejs || command -v node`" "$0"

var bower = require('bower');
var fs = require('fs');
var path = require('path');
var _ = require('lodash');

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
function processMap(pkg, outputDir) {
    var depResult = pkg._depResult;
    var pkgInfo = {
        name: pkg.pkgMeta.name,
        version: pkg.pkgMeta.version
    }
    pkgInfo.js = _.map(
        _.filter(depResult, function(elem) {
            return /.js$/.test(elem.toLowerCase());
        }), function(elem) {
            return path.join(outputDir, 'js', basename(elem));
        }
    );
    pkgInfo.css = _.map(
        _.filter(depResult, function(elem) {
            return /.css$/.test(elem.toLowerCase());
        }), function(elem) {
            return path.join(outputDir, 'css', basename(elem));
        }
    );
    pkgInfo.dependencies = [];
    // add other dependencies
    _.forEach(pkg.dependencies, function(depPkg) {
        var depMap = processMap(depPkg, outputDir);
        pkgInfo.dependencies.push(depMap);
    });
    return pkgInfo;
}


bower.commands
.list({})
.on('end', function (result) {
    console.log('Listing finished.');

    var outputDir = 'deform/static/dist';

    // get the dependencies
    var deps = processDependencies(result);
    
    // separate js and css
    var jsDeps = _.filter(deps, function(elem) {
        return /.js$/.test(elem.toLowerCase());
    });
    var cssDeps = _.filter(deps, function(elem) {
        return /.css$/.test(elem.toLowerCase());
    });

    // Copy the files.
    _.forEach(jsDeps, function(elem) {
        fs.createReadStream(elem)
            .pipe(fs.createWriteStream(path.join(outputDir, 'js', basename(elem))));
    });
    _.forEach(cssDeps, function(elem) {
        fs.createReadStream(elem)
            .pipe(fs.createWriteStream(path.join(outputDir, 'css', basename(elem))));
    });

    console.log('Copied resources to ' + outputDir);

    var map = processMap(result, outputDir);
    var outputFilename = path.join(outputDir, 'map.json');
    var formatted = JSON.stringify(map, null, 4);

    fs.writeFile(outputFilename, formatted, function(err) {
        if (err) {
            console.log('File write error:', err);
            process.exit(1);
        } else {
            console.log("JSON saved to " + outputFilename);
            console.log('OK');
        }
    });
})
.on('error', function (error) {
    console.log('Bower error:', error);
    process.exit(1);
});




