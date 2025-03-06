WebSocket Server Architecture
========================================
This document provides an overview of the WebSocket server's architecture, which manages real-time player interactions, game state synchronization, and Redis-based event handling.

----------------------------------------
Overview
----------------------------------------
The WebSocket server enables multiplayer gameplay by:
- Managing WebSocket connections for players.
- Synchronizing game state updates across all clients.
- Handling Redis-based event broadcasting to ensure seamless communication.

**Matchmaking & Room Management**
   - Players request matchmaking via `/api/pong/matchmaking/`
   - The matchmaking API assigns them to a room or creates a new one.
   - Player information is stored in Redis, and a `player_joined` event is published.
   - When a room is full, a `start_game` event is triggered.

**WebSocket Communication**
   - Players establish WebSocket connections using their `room_id` and `player_id`.
   - The `handler` function manages all WebSocket messages and routes them accordingly.
   - Messages are broadcasted to all players in a room via `broadcast_to_room()`.

**Redis Integration for Game Events**
   - Redis acts as a real-time event broker.
   - The server listens for Redis events such as `start_game` and `update_position`.
   - Events are forwarded to WebSocket-connected players.

**Handling Player Actions**
   - Players send movement updates using WebSockets (`player_move`).
   - The server validates and synchronizes these updates across all clients.
   - Score updates and eliminations are processed and broadcasted.

**WebSocket Connection Handler**
   Manages WebSocket connections, processes incoming messages, and routes events.

   Responsibilities:
   - Handles player authentication and registration.
   - Routes WebSocket messages to the appropriate event handlers.
   - Cleans up connections when players disconnect.

   Main Functions:
   - `handler(websocket, path)`: Manages WebSocket connections per player.
   - `process_incoming_event(data, websocket)`: Routes incoming messages to game logic.

----------------------------------------

**Room Manager**
   Tracks active game rooms and manages player connections.

   Responsibilities:
   - Registers new players and assigns them to rooms.
   - Tracks connected players in each room.
   - Notifies all players when someone joins or leaves.
   - Cleans up room data when all players leave.

   Main Functions:
   - `register_player(websocket, room_id, player_id, username)`: Registers a player.
   - `unregister_player(websocket, room_id, player_id)`: Handles player disconnection cleanup.

----------------------------------------

**Game Manager**
   Handles game sessions, player interactions, and game updates.

   Responsibilities:
   - Manages active game instances.
   - Updates game state at a fixed interval.
   - Handles player scoring, eliminations, and game-ending logic.

   Main Functions:
   - `create_game(room_id, players)`: Creates a new game session.
   - `start_game(room_id)`: Starts the game when all players are ready.
   - `update_games(delta_time)`: Updates game state at a fixed interval.
   - `cleanup_game(room_id)`: Cleans up inactive game sessions.

----------------------------------------

**Redis Listener**
   Listens for game-related events on Redis and dispatches them accordingly.

   Responsibilities:
   - Subscribes to Redis event channels (loaded from config).
   - Processes incoming Redis messages and forwards them to WebSocket clients.
   - Ensures real-time synchronization across all players.

   Main Function:
   - `start_redis_listener()`: Starts the Redis listener loop.

----------------------------------------

**Redis Utility Functions**
   Provides helper functions for Redis-based event handling.

   Responsibilities:
   - Publishes game events to Redis channels.
   - Sends messages to all players in a room.
   - Broadcasts messages while excluding the sender.

   Main Functions:
   - `publish_to_redis(channel, message)`: Publishes a message to Redis.
   - `notify_players(room_id, message)`: Sends a message to all players in a room.
   - `broadcast_to_room(room_id, message, exclude=None)`: Broadcasts a message to all players except the sender.

----------------------------------------
Redis Event Channels
----------------------------------------
The WebSocket server listens for specific Redis event channels. These channels define the types of events the server should process.
REDIS_CHANNELS = { "game_events": [ "start_game", "update_position", "ball_update", "ball_spawn", "start_game_countdown", "ball_despawn", "player_eliminated", "game_over" ] }
Why Use Redis for Game Events?
- Decouples WebSocket communication from game state logic.
- Ensures real-time event handling across distributed systems.
- Optimizes message passing and state synchronization.

----------------------------------------
Game Flow: How It Works
----------------------------------------

1. **Players Connect** → Players establish WebSocket connections and request to join a room.
2. **Room Assignment** → Players are assigned to an available room, and their details are stored.
3. **Game Start** → When all players are present, Redis publishes a `start_game` event.
4. **Gameplay & Updates** → Players send movement data; updates are processed and synchronized.
5. **Event Processing** → Redis handles events like `ball_update`, `score_update`, and `game_over`.
6. **Game End & Cleanup** → When a game ends, the server cleans up room data and prepares for the next match.


----------------------------------------
Final Notes
----------------------------------------
This document serves as an overview of the WebSocket server's architecture. For further implementation details, refer to the individual module files.