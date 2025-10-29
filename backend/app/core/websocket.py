"""
WebSocket connection handling for real-time updates.

This module provides WebSocket functionality for real-time room status
and admission updates across user sessions.
"""

import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        # Store connections by room for targeted updates
        self.room_connections: Dict[int, Set[WebSocket]] = {}
        # Store connections by user for targeted updates
        self.user_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from room connections
        for room_id, connections in self.room_connections.items():
            connections.discard(websocket)
            if not connections:
                del self.room_connections[room_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all active connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(message)
                else:
                    disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_user(self, message: str, user_id: int):
        """Send a message to all connections for a specific user."""
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(message)
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, user_id)
    
    async def send_to_room(self, message: str, room_id: int):
        """Send a message to all connections monitoring a specific room."""
        if room_id in self.room_connections:
            disconnected = []
            for connection in self.room_connections[room_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(message)
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error sending to room {room_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    def subscribe_to_room(self, websocket: WebSocket, room_id: int):
        """Subscribe a connection to room updates."""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(websocket)
    
    def unsubscribe_from_room(self, websocket: WebSocket, room_id: int):
        """Unsubscribe a connection from room updates."""
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]


# Global connection manager instance
manager = ConnectionManager()


class WebSocketService:
    """Service class for WebSocket operations."""
    
    @staticmethod
    async def send_room_status_update(room_id: int, status: str, room_data: dict = None):
        """Send room status update to all connected clients."""
        message = {
            "type": "room_status_update",
            "room_id": room_id,
            "status": status,
            "room_data": room_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await manager.send_to_room(json.dumps(message), room_id)
        logger.info(f"Sent room status update for room {room_id}: {status}")
    
    @staticmethod
    async def send_admission_update(admission_id: int, status: str, admission_data: dict = None):
        """Send admission update to all connected clients."""
        message = {
            "type": "admission_update",
            "admission_id": admission_id,
            "status": status,
            "admission_data": admission_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await manager.broadcast(json.dumps(message))
        logger.info(f"Sent admission update for admission {admission_id}: {status}")
    
    @staticmethod
    async def send_room_availability_update(room_id: int, available: bool):
        """Send room availability update to all connected clients."""
        message = {
            "type": "room_availability_update",
            "room_id": room_id,
            "available": available,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await manager.send_to_room(json.dumps(message), room_id)
        logger.info(f"Sent room availability update for room {room_id}: {available}")
    
    @staticmethod
    async def send_active_admissions_update(admissions_data: list):
        """Send active admissions update to all connected clients."""
        message = {
            "type": "active_admissions_update",
            "admissions": admissions_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await manager.broadcast(json.dumps(message))
        logger.info(f"Sent active admissions update: {len(admissions_data)} admissions")


async def websocket_endpoint(websocket: WebSocket, user_id: int = None):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_room":
                room_id = message.get("room_id")
                if room_id:
                    manager.subscribe_to_room(websocket, room_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscription_confirmed",
                            "room_id": room_id,
                            "timestamp": asyncio.get_event_loop().time()
                        }),
                        websocket
                    )
            
            elif message.get("type") == "unsubscribe_room":
                room_id = message.get("room_id")
                if room_id:
                    manager.unsubscribe_from_room(websocket, room_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "unsubscription_confirmed",
                            "room_id": room_id,
                            "timestamp": asyncio.get_event_loop().time()
                        }),
                        websocket
                    )
            
            elif message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
