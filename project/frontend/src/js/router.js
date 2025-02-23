import Auth from './auth.js';

class Router {


    constructor(view) {

        // Load the correct view when the page loads or the URL changes
        window.addEventListener('load', () => {this.handleRoute()});
        window.addEventListener('hashchange', () => {this.handleRoute()});
        if (!view) {
           view = '/';
        }
        this.previousView = null;
        this.currentView = view;
        this.routes = new Map();
        this.modules = [];
    }

    add(hash, target, requiresAuth, title, scripts){
        this.routes.set(hash, {
            hash: hash,
            target: target,
            requiresAuth: requiresAuth,
            title: title,
            scripts: [...scripts],
        });
    }

    static navigateTo(view)
    {
        window.location.hash = view;  // This changes the URL hash, triggering the route handling
    }
    
    handleRoute() {
        const newView = window.location.hash;
        // if (this.currentView === 'gamePong' && newView !== 'gamePong')
        //     disconnectWebSocket();
        // else if (this.currentView === 'matchmaking' && newView !== 'gamePong')
        //     disconnectWebSocket();
        if (newView === this.currentView) {
            return ;
        }
        this.previousView = this.currentView;
        this.currentView = newView;
        this.loadView();
    }

    async loadComponents() {
        // Views
        const components = document.getElementsByClassName("ft-comp");
        for (let i = 0; i < components.length; i += 1) {
            const element = components.item(i);

            const target = (() => {
                for (let j = 0; j < element.classList.length; j += 1){
                    const cls = element.classList.item(j);
                    if (cls.startsWith('ft-comp-')) {
                        return cls.replace('ft-comp-', '');
                    }
                }
                return '404';
            })();
            
            const response = await fetch(`/views/${target}.html`);
            if (!response.ok) {
                console.log(`Unable to load component ${target}.html`); //TODO: display message to notify page not found
                throw Error(`Unable to load component ${target}.html`);
            }
            const html = await response.text();
            element.innerHTML = html;
            
            const script = `./views/${target}.js`;
            try {
                const module = await import(script);
                module.load();
                this.modules.push(module);
            } catch (error) {
                console.log(`Unable to import ${script}: ${error}`);
            }
        }

        // Buttons
        const buttons = document.getElementsByClassName('ft-btn');

        for (let i = 0; i < buttons.length; i += 1) {
            const btn = buttons[i];
            btn.classList.forEach((cls) => {
                if (!cls.startsWith('ft-btn-link-')) {
                    return ;
                }
                const target = cls.replace('ft-btn-link-', '');
                btn.addEventListener('click', () => {Router.navigateTo(target)});
            });           
        }

    }

    async loadView() {
        // Check if valid route
        if (!this.routes.has(this.currentView))
        {
            console.log(`Page ${this.currentView} not found.`); //TODO: display message to notify page not found
            Router.navigateTo('#404');
            return;
        }
        const route = this.routes.get(this.currentView);
        try {
            // If route requires auth, check token status.
            if (route.requiresAuth) {
                const isTokenValid = await Auth.silentRefresh();
                if (!isTokenValid) {
                    console.log("Token is invalid or expired. Please login again."); //TODO: display message to notify token invalid
                    Router.navigateTo('login');
                    return;
                }
            }

            // Load in html view template
            const response = await fetch(route.target);
            if (!response.ok) {
                console.log('Page not found. Back to top page.'); //TODO: display message to notify page not found
                Router.navigateTo('');
                return;
            }
            const html = await response.text();
            document.title = `${route.title} - Pong Games`;
            document.getElementById('app').innerHTML = html;

            // Load nested components and buttons
            this.loadComponents();
            for (const script_location of route.scripts) {
                const module = await import(script_location);
                module.load();
                this.modules.push(module);
            }
            

    
            // // After loading the view, set up the appropriate form handlers
            // if (this.currentView == 'welcome') {
            //     return ;
            // } else {
            //     if (view == 'home') {
            //         const { setupHome } = await import('./home.js');
            //         setupHome();
            //     }
            //     else if (view === 'game_matchmaking') {
            //         await import('./WebSocketService.js');
            //         const { setupMatchmaking } = await import('./matchmaking.js');
            //         setupMatchmaking();
            //     }
            //     else if (view === 'gamePong') {
            //         const { initPong } = await import('./games/gamePong/js/main.js');
            //         initPong();
            //     }
            // }
        } catch (error) {
            console.error('Error loading view:', error);
            document.getElementById('app').innerHTML = '<p>Error loading view.</p>';
        }
    }
    
}



export default Router