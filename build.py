
from glob import glob
import re
import sys
from os.path import exists
import os

if 'D3_PATH' in os.environ:
    D3_PATH = os.environ['D3_PATH']
else:
    D3_PATH = './d3/'

MOD_START = [
    'polyfills.js',
    D3_PATH + 'src/start.js',
    'core.module.js'
]

MOD_END = [
    D3_PATH + 'src/end.js'
]


def error(msg):
    sys.stderr.write('ERROR: '+msg+'\n')
    sys.exit(-1)


def main():
    targets = sys.argv[1:]
    if len(targets) == 0:
        error("you need to specify what you want, e.g. 'd3.layout.treemap'")

    modules = parse_dependencies()
    visited = []
    deps = []
    for m in targets:
        if m in modules:
            deps.append(m)
        else:
            error('ignoring unknown module: ' + m)

    i = 0
    while i < len(deps):
        m = deps[i]
        visited.append(m)
        #if m == 'd3.rgb':
        #    sys.stderr.write(', '.join(deps)+'\n\n')
        for req in modules[m]['depends']:
            if req != 'd3' and req not in visited:
                if req in deps:
                    deps = filter(lambda k: k != req, deps)
                deps.append(req) # add to required packages
        i += 1
    # remove double dependencies
    deps.reverse()

    files = MOD_START
    for m in deps:
        m = m.split('.')[1:]
        chk = []
        if len(m) == 1:
            chk.append('core/' + m[0] + '.js')  # e.g. src/core/merge.js
            chk.append(m[0] + '/' + m[0] + '.js')  # e.g. src/geo/geo.js
        elif len(m) == 2:
            chk.append('core/' + m[0] + '-' + m[1] + '.js')  # src/core/format-locale.js
            chk.append(m[0] + '/' + m[1] + '.js')  # src/layout/bundle.js
        elif len(m) == 3:
            chk.append(m[0] + '/' + m[1] + '-' + m[2] + '.js')  # src/layout/bundle.js
        else:
            error('not handled yet: ' + m)
        found = False
        for f in chk:
            if exists(D3_PATH + 'src/' + f):
                files.append(D3_PATH + 'src/' + f)
                found = True
                break
        if not found:
            error('not found: ' + m)
    files += MOD_END
    out = ""
    for f in files:
        fo = open(f, 'r')
        out += fo.read()
        fo.close()
    print out


def parse_dependencies():
    d3_mod = re.compile('(d3(?:\.[a-zA-Z]+)+)')
    d3_func_def = re.compile('function +(d3(?:_[a-zA-Z]+)+)')
    d3_func_call = re.compile('(?!function +)(d3(?:_[a-zA-Z]+)+)')

    modules = {}

    alias = {
        'd3.select': 'd3.selection.root',
        'd3.selectAll': 'd3.selection.root',
        'd3.tsv': 'd3.dsv.tsv',
        'd3.csv': 'd3.dsv.csv',
        'd3.interpolateArray': 'd3.interpolate',
        'd3.interpolateNumber': 'd3.interpolate',
        'd3.interpolateRgb': 'd3.interpolate',
        'd3.interpolateString': 'd3.interpolate',
        'd3.interpolateObject': 'd3.interpolate',
        'd3.interpolators': 'd3.interpolate',
        'd3.interpolateTransform': 'd3.interpolate',
        'd3.interpolateHcl': 'd3.interpolate',
        'd3.interpolateLab': 'd3.interpolate',
        'd3.interpolateHsl': 'd3.interpolate',
        'd3.interpolateRound': 'd3.interpolate',
        'd3.bisector': 'd3.bisect',
        'd3.bisectLeft': 'd3.bisect',
        'd3.bisectRight': 'd3.bisect',
        'd3.time.months': 'd3.time.month',
        'd3.time.month.utc': 'd3.time.month',
        'd3.time.minutes': 'd3.time.minute',
        'd3.time.minute.utc': 'd3.time.minute',
        'd3.time.seconds': 'd3.time.second',
        'd3.time.second.utc': 'd3.time.second',
        'd3.time.hours': 'd3.time.hour',
        'd3.time.hour.utc': 'd3.time.hour',
        'd3.time.days': 'd3.time.day',
        'd3.time.day.utc': 'd3.time.day',
        'd3.time.years': 'd3.time.year',
        'd3.time.year.utc': 'd3.time.year',
        'd3.time.sunday': 'd3.time.week',
        'd3.time.sunday.utc': 'd3.time.week',
        'd3.time.weeks': 'd3.time.week',
        'd3.time.weeks.utc': 'd3.time.week',
        'd3.time.weekOfYear': 'd3.time.week',
    }

    d3_is_mod = re.compile('d3(?:\.[a-zA-Z]+)*(\.[a-zA-Z]+)\\1')

    for f in glob(D3_PATH + 'src/*/*.js'):
        src = open(f).read()
        f = f[len(D3_PATH):]
        cl = 'd3.%s' % f[4:-3].replace('core/', '').replace('-', '.').replace('/', '.')
        if d3_is_mod.match(cl):
            cl = cl[:cl.rfind('.')]

        if cl == "d3.core":
            cl = "d3"

        module = modules[cl] = dict(defines=[], uses=[], depends=[], calls=[], len=len(src))

        # at least a module is dependend on its own namespace
        parts = cl.split('.')
        if len(parts) > 2:
            module['depends'].append('.'.join(parts[:-1]))

        for mod in d3_mod.findall(src):
            if mod != cl:
                module['uses'].append(mod)

        for func in d3_func_def.findall(src):
            module['defines'].append(func)

        for func in d3_func_call.findall(src):
            if func not in module['defines']:
                module['calls'].append(func)

    for m in modules:
        mod = modules[m]
        for need in mod['uses']:
            if not need in modules:
                if need in alias:
                    need = alias[need]
                parent = need[:need.rfind('.')]
                if parent in modules:
                    need = parent
                elif parent in alias and alias[parent] in modules:
                    need = alias[parent]
            if need not in modules:
                #print 'missing', need
                continue
            if need not in mod['depends'] and need != m and need != 'd3':
                mod['depends'].append(need)

        for func in mod['calls']:
            # find mod who provides func
            for m1 in modules:
                if m1 != m:
                    if func in modules[m1]['defines'] and m1 not in mod['depends'] and m1 != m:
                        mod['depends'].append(m1)
    import json
    open('deps.json', 'w').write(json.dumps(modules, indent=2, separators=(',', ':')))
    return modules


if __name__ == '__main__':
    main()
