/* eslint-disable */

const fs = require('fs');
const path = require('path');

const acc = {
    'id': 0,
    'name': 'apify-client',
    'kind': 1,
    'kindString': 'Project',
    'flags': {},
    'originalName': '',
    'children': [],
    'groups': [],
    "comment": {
        "summary": [
            {
                "kind": "text",
                "text": "# Apify Client for Python\nApify Client for Python is a library for controlling your actors on the Apify Platform from Python. It is a thin wrapper around the [Apify API](https://docs.apify.com/api/v2). The library is available on [PyPI](https://pypi.org/project/apify-client/) and can be installed using `pip install apify-client`."
            },
        ]
    },
    "sources": [
        {
            "fileName": "src/index.ts",
            "line": 1,
            "character": 0,
            "url": "https://github.com/apify/apify-client-python/blob/123456/src/dummy.py"
        }
    ]
};

let oid = 1;

function plural(word) {
    const plurals = {
        'Class': 'Classes',
        'Method': 'Methods',
        'Constructor': 'Constructors',
        'Property': 'Properties',
        'Enumeration': 'Enumerations',
        'Enumeration Member': 'Enumeration Members',
    }

    return plurals[word];
}

const kinds = {
    'class': {
        kind: 128,
        kindString: 'Class',
    },
    'function': {
        kind: 2048,
        kindString: "Method",
    },
    'data': {
        kind: 1024,
        kindString: 'Property',
    },
    'enum': {
        kind: 8,
        kindString: "Enumeration",
    },
    'enumValue': {
        kind: 16,
        kindString: "Enumeration Member",
    },
}

function stripOptional(s) {
    return s ? s.replace(/(Optional|\[|\])/g, '') : null;
}

function isCustomClass(s) {
    return !['dict', 'list', 'str', 'int', 'float', 'bool'].includes(s.toLowerCase());
}

function inferType(x) {
    return !isCustomClass(stripOptional(x) ?? '') ? {
        type: 'intrinsic',
        name: stripOptional(x) ?? 'void',
    } : {
        type: 'reference',
        name: stripOptional(x),
    }
}

function traverse(o, parent) {
    for( let x of o.members ?? []) {
        console.log(x.name);
        let typeDocType = kinds[x.type];

        if(x.bases?.includes('Enum')) {
            typeDocType = kinds['enum'];
        }

        let type = inferType(x.datatype);

        if(parent.kindString === 'Enumeration') {
            typeDocType = kinds['enumValue'];
            type = {
                type: 'literal',
                value: x.value,
            }
        }

        if(x.type in kinds) {

            let newObj = {
                id: oid++,
                name: x.name,
                ...typeDocType,
                flags: {},
                comment: x.docstring ? {
                    summary: [{
                        kind: 'text',
                        text: x.docstring?.content,
                    }],
                } : undefined,
                type,
                children: [],
                groups: [],
            };

            if(newObj.kindString === 'Method') {
                newObj.signatures = [{
                    id: oid++,
                    name: x.name,
                    kind: 4096,
                    kindString: 'Call signature',
                    flags: {},
                    type: inferType(x.return_type),
                    parameters: x.args.map((p) => (p.name === 'self' ? undefined : {
                        id: oid++,
                        name: p.name,
                        kind: 32768,
                        kindString: 'Parameter',
                        flags: {
                            isOptional: p.datatype?.includes('Optional'),
                        },
                        type: inferType(p.datatype),
                    })).filter(x => x),
                }];
            }

            if(newObj.name === '__init__') {
                newObj.kindString = 'Constructor';
                newObj.kind = 512;
            }

            traverse(x, newObj);

            const group = parent.groups.find((g) => g.title === plural(newObj.kindString));
            if(group) {
                group.children.push(newObj.id);
            } else {
                parent.groups.push({
                    title: plural(newObj.kindString),
                    children: [newObj.id],
                });
            }

            parent.children.push(newObj);
        }
    }
}

function main() {
    const argv = process.argv.slice(2);

    const rawdump = fs.readFileSync(argv[0], 'utf8');
    const modules = rawdump.split('\n').filter((line) => line !== '');   

    for (const module of modules) {
        const o = JSON.parse(module);

        traverse(o, acc);
    };

    // recursively fix references (collect names->ids of all the named entities and then inject those in the reference objects)
    const names = {};
    function collectIds(o) {
        for (const child of o.children ?? []) {
            names[child.name] = child.id;
            collectIds(child);
        }
    }
    collectIds(acc);
    
    function fixRefs(o) {
        for (const child of o.children ?? []) {
            if (child.type?.type === 'reference') {
                child.type.id = names[child.type.name];
            }
            if (child.signatures) {
                for (const sig of child.signatures) {
                    for (const param of sig.parameters ?? []) {
                        if (param.type?.type === 'reference') {
                            param.type.id = names[param.type.name];
                        }
                    }
                    if (sig.type?.type === 'reference') {
                        sig.type.id = names[sig.type.name];
                    }
                }
            }
            fixRefs(child);
        }
    }
    fixRefs(acc);

    fs.writeFileSync(path.join(__dirname, 'api-typedoc-generated.json'), JSON.stringify(acc, null, 2));
}

main();
