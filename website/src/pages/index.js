import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import CodeBlock from '@theme/CodeBlock';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

import HomePageExample from '!!raw-loader!./home_page_example.py';

function Hero() {
    return (
        <header className={clsx('container', styles.heroBanner)}>
            <div className="row padding-horiz--md">
                <div className="col col--7">
                    <div className={clsx(styles.relative, 'row')}>
                        <div className="col">
                            <h1 className={styles.tagline}>
                                Apify API client for Python
                            </h1>
                            <h1 className={styles.tagline}>
                                {/* eslint-disable-next-line max-len */}
                                <span>Apify API client</span> for Python.
                            </h1>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <h2></h2>
                            <h2>
                                The Apify API Client for Python is the official library to access Apify API from your Python applications.
                                It provides useful features like automatic retries and convenience functions to improve your experience with the Apify API.
                            </h2>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <div className={styles.heroButtons}>
                                <Link to="docs/overview/introduction" className={styles.getStarted}>Get Started</Link>
                                <iframe src="https://ghbtns.com/github-btn.html?user=apify&repo=apify-client-python&type=star&count=true&size=large" width="170" height="30" title="GitHub"></iframe>
                            </div>
                        </div>
                    </div>
                </div>
                <div className={clsx(styles.relative, 'col', 'col--5')}>
                    <div className={styles.logoBlur}>
                        <img src={useBaseUrl('img/logo-blur.png')} className={clsx(styles.hideSmall)} />
                    </div>
                    <div className={styles.codeBlock}>
                        <CodeBlock className="language-bash">
                            pip install apify-client
                        </CodeBlock>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default function Home() {
    const { siteConfig } = useDocusaurusContext();
    return (
        <Layout
            description={siteConfig.description}>
            <Hero />
            <div>
                <div className="container">
                    <div className="row padding-horiz--md" >
                        <div className="col col--4">
                            <p style={{ lineHeight: '200%' }}>
                            For example, the Apify API Client for Python makes it easy to run your own Actors or Actors from the <a href='https://apify.com/store'>Apify Store</a>
                                {' '}by simply using the <code>.call()</code> method to start an Actor and wait for it to finish.
                            </p>
                        </div>
                        <div className="col col--8">
                            <CodeBlock className="language-python">{HomePageExample}</CodeBlock>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
