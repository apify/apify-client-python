#!/usr/bin/node

const { execSync } = require('child_process');
const { readFileSync, writeFileSync } = require('fs');
const path = require('path');

const referencePath = `${__dirname}/docs/reference/`;

const tree = JSON.parse(execSync(`tree -Jf ${referencePath}`, { encoding: 'utf8' }));
const includePaths = [{
    path: "apify_client/clients/resource_clients",
    label: "Resource Clients",
}, {
    path: "apify_client",
    label: "Helper Classes",
}];

function capitalize(s) {
    return s[0].toUpperCase() + s.slice(1);
}

function generateSidebarItems(tree, includePaths, acc) {
    if (tree.type === 'directory') {
        const x = includePaths.find(({ path }) => tree.name.endsWith(path));
        if(x){
            acc.push({
                type: 'category',
                label: x.label,
                items: tree.contents.filter(x => x.type === "file").map(x => x.name),
            });
        }
        tree.contents.filter(x => x.type === "directory").forEach(x => generateSidebarItems(x, includePaths, acc));
    }
}

const acc = [{
    "type": "doc",
    "id": "reference/index"
}];
generateSidebarItems(tree[0], includePaths, acc);

acc.sort((a,b) => includePaths.findIndex(x => x.label === a.label) - includePaths.findIndex(x => x.label === b.label));

for (const category of acc) {
    for (let [i,p] of Object.entries(category.items ?? [])){
        let newPath = p;

        // docusaurus treats files starting with _ as hidden (partial docs)
        if (path.basename(p).startsWith('_')){
            newPath = path.join(path.dirname(p), path.basename(p).slice(1));
        }

        const content = readFileSync(`${p}`, { encoding: 'utf8' });
        const sidebarLabel = content.match(/sidebar_label:.*/)[0].split(':')[1].trim();
        const newLabel = sidebarLabel.split("_").filter(x => x).map(capitalize).join(" ");
        let newContent = content
                    .replace(/sidebar_label:.*/, `sidebar_label: ${newLabel}`)
                    .replace(/title:.*/, `title: ${newLabel}`);
        writeFileSync(newPath, newContent);

        newPath = newPath.slice(newPath.lastIndexOf('docs/reference/')+5).replace('.md', '');

        category.items[i] = newPath;
    }
}

writeFileSync(path.join(referencePath, 'sidebar.json'), JSON.stringify(acc, null, 2));
