const { join, resolve } = require('node:path');

const { config } = require('@apify/docs-theme');

const { externalLinkProcessor } = require('./tools/utils/externalLink');
const versions = require('./versions.json');

const GROUP_ORDER = [
    'Apify API clients',
    'HTTP clients',
    'Resource clients',
    'Errors',
    'Models',
    'Typed dicts',
    'Other',
];

const groupSort = (g1, g2) => {
    const i1 = GROUP_ORDER.indexOf(g1);
    const i2 = GROUP_ORDER.indexOf(g2);
    // Both known – sort by defined order
    if (i1 !== -1 && i2 !== -1) return i1 - i2;
    // Unknown groups go after known ones
    if (i1 !== -1) return -1;
    if (i2 !== -1) return 1;
    // Both unknown – alphabetical
    return g1.localeCompare(g2);
};

const { absoluteUrl } = config;

/** @type {Partial<import('@docusaurus/types').DocusaurusConfig>} */
module.exports = {
    future: {
        faster: {
            swcJsLoader: true,
            swcJsMinimizer: true,
            swcHtmlMinimizer: true,
            lightningCssMinimizer: true,
            rspackBundler: true,
            mdxCrossCompilerCache: true,
            rspackPersistentCache: true,
        },
        v4: {
            removeLegacyPostBuildHeadAttribute: true,
            useCssCascadeLayers: false,
        },
    },
    title: 'API client for Python | Apify Documentation',
    url: absoluteUrl,
    baseUrl: '/api/client/python',
    trailingSlash: false,
    organizationName: 'apify',
    projectName: 'apify-client-python',
    favicon: 'img/favicon.ico',
    scripts: ['/js/custom.js', ...(config.scripts ?? [])],
    onBrokenLinks:
    /** @type {import('@docusaurus/types').ReportingSeverity} */ ('warn'),
    onBrokenMarkdownLinks:
    /** @type {import('@docusaurus/types').ReportingSeverity} */ ('warn'),
    themes: [
        [
            '@apify/docs-theme',
            {
                changelogFromRoot: true,
                changelogDisplayedSidebar: `sidebar`,
                subNavbar: {
                    title: 'API Client for Python',
                    items: [
                        {
                            type: 'doc',
                            docId: 'introduction/introduction',
                            label: 'Docs',
                            position: 'left',
                            activeBaseRegex: '/docs(?!/changelog)',
                        },
                        {
                            type: 'custom-versioned-reference',
                            label: 'Reference',
                            position: 'left',
                            activeBaseRegex: '/reference',
                        },
                        {
                            type: 'doc',
                            docId: 'changelog',
                            label: 'Changelog',
                            position: 'left',
                            activeBaseRegex: '/docs/changelog',
                        },
                        {
                            href: 'https://github.com/apify/apify-client-python',
                            label: 'GitHub',
                            position: 'left',
                        },
                        {
                            type: 'docsVersionDropdown',
                            position: 'left',
                            className: 'navbar__item',
                            'data-api-links': JSON.stringify([
                                'reference/next',
                                ...versions.map((version, i) => (i === 0 ? 'reference' : `reference/${version}`)),
                            ]),
                            dropdownItemsBefore: [],
                            dropdownItemsAfter: [],
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
                    editUrl: 'https://github.com/apify/apify-client-python/blob/master/website/',
                },
            }),
        ],
    ]),
    plugins: [
        [
            '@apify/docusaurus-plugin-typedoc-api',
            {
                projectRoot: '.',
                changelogs: false,
                readmes: false,
                packages: [{ path: '.' }],
                typedocOptions: {
                    excludeExternals: false,
                },
                sortSidebar: groupSort,
                routeBasePath: 'reference',
                python: true,
                pythonOptions: {
                    pythonModulePath: join(__dirname, '../src/apify_client'),
                    moduleShortcutsPath: join(__dirname, 'module_shortcuts.json'),
                },
            },
        ],
        [
            resolve(__dirname, 'src/plugins/docusaurus-plugin-segment'),
            {
                writeKey: process.env.SEGMENT_TOKEN,
                allowedInDev: false,
            },
        ],
        [
            '@signalwire/docusaurus-plugin-llms-txt',
            {
                content: {
                    includeVersionedDocs: false,
                    enableLlmsFullTxt: true,
                    includeBlog: true,
                    includeGeneratedIndex: false,
                    includePages: true,
                    relativePaths: false,
                    excludeRoutes: [
                        '/api/client/python/reference/[0-9]*/**',
                        '/api/client/python/reference/[0-9]*',
                        '/api/client/python/reference/next/**',
                        '/api/client/python/reference/next',
                    ],
                },
            },
        ],
        ...config.plugins,
    ],
    themeConfig: {
        ...config.themeConfig,
        versions,
        tableOfContents: {
            ...config.themeConfig.tableOfContents,
            maxHeadingLevel: 5,
        },
        footer: {
            ...config.themeConfig.footer,
            logo: {
                ...config.themeConfig.footer.logo,
                href: 'docs',
            },
        },
    },
    staticDirectories: ['node_modules/@apify/docs-theme/static', 'static'],
    customFields: {
        ...(config.customFields ?? []),
    },
};
