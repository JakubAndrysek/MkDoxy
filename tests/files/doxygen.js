#!/usr/bin/env node
var fs = require('fs')

var functionName = /^\s+\/\/\/\s+@function\s+(.*)$/;
var type = /^(\s+)\/\/\/\s+@param\s+{(\w*)}\s+(.+?)(\s+.*)$/;
var param = /^(\s+)\/\/\/\s+@param\s+(.+?)\s/;
var resultType = /^(\s+)\/\/\/\s+@return\s+{(\w+)}(\s+.*)$/;

function Section()
{
	this.name = '';
	this.result = 'undefined';
	this.args = [];
	this.comments = [];
	this.namespaces = [];
}

Section.prototype.handle_function = function (line) {
	this.namespaces = line.match(functionName)[1].split('.') || [];
	this.name = this.namespaces.pop();
};

Section.prototype.handle_param = function (line) {
	var paramType = 'Object';
	var name = '';
	var m = line.match(type);
	var r = line;
	if (m) {
		paramType = m[2];
		name = m[3];
		r = m[1] + '/// @param ' + name + m[4];
	}
	else {
		m = line.match(param);
		name = m[2];
	}
	this.args.push({name: name, type: paramType});
	this.comments.push(r);
};

Section.prototype.handle_return = function (line) {
	this.result = 'undefined';
	var m = line.match(resultType);
	var r = line;
	if (m) {
		this.result = m[2];
		r = m[1] + '/// @return ' + m[3];
	}
	this.comments.push(r);
};

Section.prototype.Generate = function () {
	var doc = [];

	this.namespaces.forEach(function (namespace) {
		doc.push('namespace ' + namespace + ' {\n');
	});

	this.comments.forEach(function (c) {
		doc.push(c);
	});

	var args = [];

	this.args.forEach(function (argument) {
		args.push(argument.type + ' ' + argument.name);
	});

	if (this.name) {
		doc.push(this.result + ' ' + this.name + '(' + args.join(', ') + ');');
	}

	this.namespaces.forEach(function (namespace) {
			doc.push('}\n');
	});
	return doc.join('\n');
};

Section.prototype.handle_line = function (line) {
	this.comments.push(line);
};

function writeLine(line) {
	process.stdout.write(line + '\n');
}

fs.readFile(process.argv[2], 'utf8', function (err, data) {
	var lines = data.split('\n');
	var comment = /^\s*\/\/\//;
	var directive = /@(\w+)\s+(.*)$/;
	var inside = false;
	var section = new Section();
	lines.forEach(function(line) {
		if (line.match(comment)) {
			var d = line.match(directive);
			if (d) {
				var handle = Section.prototype['handle_' + d[1]] || Section.prototype.handle_line;
				handle.call(section, line);
			} else {
				section.handle_line(line);
			}
			inside = true;
		} else if (inside) {
			writeLine(section.Generate());
			inside = false;
			section = new Section();
		}
	});
});