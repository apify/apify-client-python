/* eslint-disable global-require,import/no-extraneous-dependencies */
const { config } = require('@apify/docs-theme');
const { externalLinkProcessor } = require('./tools/utils/externalLink');

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
                            to: 'docs/docs',
                            label: 'Docs',
                            position: 'left',
                            activeBaseRegex: 'docs',
                        },
                        // {
                        //     to: 'api/changelog',
                        //     label: 'Changelog',
                        //     position: 'left',
                        //     activeBaseRegex: 'changelog',
                        // },
                        {
                            type: 'docsVersionDropdown',
                            position: 'left',
                            className: 'navbar__item', // fixes margin around dropdown - hackish, should be fixed in theme
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
                },
            }),
        ],
    ]),
    themeConfig: config.themeConfig,
};