const path = require('path');

const { config } = require('@apify/docs-theme');

const { externalLinkProcessor } = require('./tools/utils/externalLink');
const { groupSort } = require('./transformDocs.js');

const { absoluteUrl } = config;

/** @type {Partial<import('@docusaurus/types').DocusaurusConfig>} */
module.exports = {
    future: {
        experimental_faster: {
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
                subNavbar: {
                    title: 'API Client for Python',
                    items: [
                        {
                            to: 'docs/overview/introduction',
                            label: 'Docs',
                            position: 'left',
                            activeBaseRegex: '/docs(?!/changelog)',
                        },
                        {
                            to: '/reference',
                            label: 'Reference',
                            position: 'left',
                            activeBaseRegex: '/reference',
                        },
                        {
                            to: 'docs/changelog',
                            label: 'Changelog',
                            position: 'left',
                            activeBaseRegex: '/docs/changelog',
                        },
                        {
                            href: 'https://github.com/apify/apify-client-python',
                            label: 'GitHub',
                            position: 'left',
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
                pathToCurrentVersionTypedocJSON: `${__dirname}/api-typedoc-generated.json`,
                sortSidebar: groupSort,
                routeBasePath: 'reference',
                python: true,
                pythonOptions: {
                    pythonModulePath: path.join(__dirname, '../src/apify_client'),
                    moduleShortcutsPath: path.join(__dirname, 'module_shortcuts.json'),
                },
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
                },
            },
        ],
        ...config.plugins,
    ],
    themeConfig: {
        ...config.themeConfig,
        tableOfContents: {
            ...config.themeConfig.tableOfContents,
            maxHeadingLevel: 5,
        },
    },
    staticDirectories: ['node_modules/@apify/docs-theme/static', 'static'],
    customFields: {
        ...(config.customFields ?? []),
    },
};
