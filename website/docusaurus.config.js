/* eslint-disable global-require,import/no-extraneous-dependencies */
const { config } = require('@apify/docs-theme');
const { externalLinkProcessor } = require('./tools/utils/externalLink');
const { groupSort } = require('./transformDocs.js');

const { absoluteUrl } = config;

/** @type {Partial<import('@docusaurus/types').DocusaurusConfig>} */
module.exports = {
    title: 'Apify Docs v2',
    tagline: 'Apify Documentation',
    url: absoluteUrl,
    baseUrl: '/client-python',
    trailingSlash: false,
    organizationName: 'apify',
    projectName: 'apify-client-python',
    scripts: ['/js/custom.js'],
    favicon: 'img/favicon.ico',
    onBrokenLinks:
    /** @type {import('@docusaurus/types').ReportingSeverity} */ ('warn'),
    onBrokenMarkdownLinks:
    /** @type {import('@docusaurus/types').ReportingSeverity} */ ('warn'),
    themes: [
        [
            '@apify/docs-theme',
            {
                subNavbar: {
                    title: 'Apify Client Python',
                    items: [
                        {
                            to: 'docs/intro',
                            label: 'Docs',
                            position: 'left',
                            activeBaseRegex: 'docs(?!/changelog)',
                        },
                        // {
                        //     type: 'docsVersionDropdown',
                        //     position: 'left',
                        //     className: 'navbar__item', // fixes margin around dropdown - hackish, should be fixed in theme
                        //     dropdownItemsBefore: [],
                        //     dropdownItemsAfter: [],
                        // },
                        {
                            to: '/api',
                            label: 'Reference',
                            position: 'left',
                            activeBaseRegex: '/api',
                        },
                        {
                            to: 'docs/changelog',
                            label: 'Changelog',
                            position: 'left',
                            activeBaseRegex: 'changelog',
                        },
                    ],
                },
            },
        ],
    ],
    presets: /** @type {import('@docusaurus/types').PresetConfig[]} */ ([
        [
            '@docusaurus/preset-classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    path: '../docs',
                    sidebarPath: './sidebars.js',
                    rehypePlugins: [externalLinkProcessor],
                },
            }),
        ],
    ]),
    plugins: [
        [
            'docusaurus-plugin-typedoc-api',
            {
                projectRoot: `.`,
                changelogs: false,
                readmes: false,
                packages: [{ path: '.' }],
                typedocOptions: {
                    excludeExternals: false,
                },
                pathToTypedocJSON: `${__dirname}/api-typedoc-generated.json`,
                sortSidebar: groupSort,
            },
        ],
    ],
    themeConfig: {
        ...config.themeConfig,
        tableOfContents: {
            ...config.themeConfig.tableOfContents,
            maxHeadingLevel: 5,
        },
    },
    staticDirectories: ['node_modules/@apify/docs-theme/static', 'static'],
};