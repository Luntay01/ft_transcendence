// Function to handle route changes based on URL fragments
import Router from "./router.js";
import Auth from "./auth.js";

function disconnectWebSocket()
{
    const ws = WebSocketService.getInstance();
    if (ws.isConnected())
        ws.disconnect();
}

const router = new Router();

router.add(
    '',
    '/views/welcome.html',
    false,
    'Welcome',
    []
);
router.add(
    '#',
    '/views/welcome.html',
    false,
    'Welcome',
    []
);

router.add(
    '#404',
    '/views/404.html',
    false,
    'Page Not Found',
    []
)

router.add(
    '#home',
    '/views/home.html',
    true,
    'Home',
    [
        './views/home.js',
    ]
);

router.add(
    '#signup',
    '/views/signup.html',
    false,
    'Signup',
    [
        './views/signup.js'
    ]
);

router.add(
    '#login',
    '/views/login.html',
    false,
    'Login',
    [
        './views/login.js'
    ]
);

router.add(
    '#profile',
    '/views/profile.html',
    true,
    'Profile',
    [
        './views/profile.js'
    ]
);

// const auth = new Auth()


