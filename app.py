import asyncio
from flask import Flask, jsonify, send_from_directory, request
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the environment variables
secret_from_viam_app = os.getenv('SECRET_FROM_VIAM_APP')
address_from_viam_app = os.getenv('ADDRESS_FROM_VIAM_APP')

app = Flask(__name__)

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=secret_from_viam_app)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(address_from_viam_app, opts)

async def move(base, velocity, distance_mm):
    await base.move_straight(velocity=velocity, distance=distance_mm)

async def turn(base, angle, velocity):
    await base.spin(angle=angle, velocity=velocity)

def execute_api_action(action):
    robot = asyncio.run(connect())
    rover_base = Base.from_robot(robot, 'viam_base')
    asyncio.run(action(rover_base))
    asyncio.run(robot.close())

    response = {
        "response": "OK",
        "status": 200,
    }
    return jsonify(response)

default_movement_velocity = 50
default_turn_velocity = 25
default_movement_distance_cm = 50
default_turn_angle = 90

@app.route('/move_forward', methods=['GET'])
def api_move_forward():
    distance_cm = int(request.args.get('distance_cm', default_movement_distance_cm))
    distance_mm = distance_cm * 10
    return execute_api_action(lambda base: move(base, default_movement_velocity, distance_mm))

@app.route('/move_backward', methods=['GET'])
def api_move_backward():
    distance_cm = int(request.args.get('distance_cm', default_movement_distance_cm))
    distance_mm = distance_cm * 10
    return execute_api_action(lambda base: move(base, -1 * default_movement_velocity, distance_mm))

@app.route('/rotate_left', methods=['GET'])
def api_rotate_left():
    turn_angle = int(request.args.get('deg', default_turn_angle))
    return execute_api_action(lambda base: turn(base, turn_angle, default_turn_velocity))

@app.route('/rotate_right', methods=['GET'])
def api_rotate_right():
    turn_angle = int(request.args.get('deg', default_turn_angle))
    return execute_api_action(lambda base: turn(base, -1 * turn_angle, default_turn_velocity))

@app.route('/.well-known/<path:path>')
def send_well_known(path):
    return send_from_directory('well-known', path)

@app.route('/misc/<path:path>')
def send_misc(path):
    return send_from_directory('misc', path)

if __name__ == '__main__':
    app.run(port=5057)
