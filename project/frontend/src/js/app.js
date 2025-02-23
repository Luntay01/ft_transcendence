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
        './views/signup.js',
    ]
);

router.add(
    '#login',
    '/views/login.html',
    false,
    'Login',
    [
        './views/login.js',
    ]
);

router.add(
    '#profile',
    '/views/profile.html',
    true,
    'Profile',
    [
        './views/profile.js',
    ]
);

router.add(
    '#gamePong',
    '/views/gamePong.html',
    true,
    'Play Pong',
    [
        './views/gamePong.js',
    ]
)

router.add(
    '#game_matchmaking',
    '/views/game_matchmaking.html',
    true,
    'Find Local Match',
    [
        // './views/WebSocketService.js',
        './views/matchmaking.js',
    ]
)

router.add(
    '#leaderboard',
    '/views/leaderboard.html',
    true,
    'Leaderboard',
    []
)

router.add(
    '#friends',
    '/views/friends.html',
    true,
    'Friends',
    []
)

router.add(
    '#match_history',
    '/views/match_history.html',
    true,
    'Match History',
    []
)


