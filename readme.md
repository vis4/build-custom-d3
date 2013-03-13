# Build your custom D3

You've been there before: sometimes the world really sucks and you just cannot use [D3](http://d3js.org)
for your awesome visualization because of backward compatiblity bla bla. So you go with
[Raphael](http://raphaeljs.com) or whatever you prefer. But wouldn't it be nice to use
just some parts of D3, say, the treemap layout or a color scale?

**Update:** With [D3 3.1.0](https://github.com/mbostock/d3/tree/3.1.0) there is a simpler way to
create custom d3 builds using the amazing [SMASH](https://github.com/mbostock/smash)™:

```bash
❯ npm install smash
❯ cd d3/
❯ cat src/start.js > d3.treemap.js
❯ smash src/layout/treemap.js >> d3.treemap.js
❯ cat src/end.js >> d3.treemap.js
```

I keep the old readme below, if you're interested.

### Deprecated readme:


```bash
❯ git clone git://github.com/gka/build-custom-d3
❯ cd build-custom-d3/
❯ git clone git://github.com/mbostock/d3.git
❯ python build.py d3.layout.treemap > d3.treemap.js
```

Et voilà, there's your custom ``d3.treemap.js``, and it's only 1.7K after minifying and gzipping:

```bash
❯ uglifyjs -m -c -o d3.treemap.min.js d3.treemap.js
❯ gzip d3.treemap.min.js
❯ ls -lh d3.treemap*
-rw-r--r--  1 you  staff    10K 13 Mar 00:52 d3.treemap.js
-rw-r--r--  1 you  staff   3.9K 13 Mar 00:52 d3.treemap.min.js
-rw-r--r--  1 you  staff   1.7K 13 Mar 00:54 d3.treemap.min.js.gz
```

Now let's go and compute a layout in node.js:

```bash
❯ node
> require('./d3.treemap')
{}
> tree = { children: [{ value: 10 }, { value: 20 }] }
{ children: [ { value: 10 }, { value: 20 } ] }
> d3.layout.treemap().size([200,200])(tree)
[ { children: [ [Object], [Object] ],
    depth: 0, value: 30, x: 0, y: 0, dx: 200, dy: 200, area: 40000
  },
  { value: 10, depth: 1, area: 13333, x: 0, y: 0, dy: 200, dx: 67 },
  { value: 20, depth: 1, area: 26666, x: 67, y: 0, dy: 200, dx: 133, z: true }
]
```

You can build several "modules" at once, too:

```bash
❯ python build.py d3.layout.treemap d3.layout.pie > d3.build.js
```

If D3 already lives somewhere else on your computer, you can set the D3_PATH environment var:

```bash
❯ export D3_PATH=/path/to/my/d3
```

Also, here's a handy one-liner for testing the script:

```bash
❯ python build.py d3.lab | node -p
{ version: '3.0.8',
  hsl: [Function],
  map: [Function],
  hcl: [Function],
  rgb: [Function],
  lab: [Function] }
```


