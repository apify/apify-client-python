import { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

export default function Home() {
    const history = useHistory();

    useEffect(() => {
        history.replace('/api/client/python/docs/introduction/overview');
    }, [history]);

    return null;
}
