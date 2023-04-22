import asyncio
from flask import Flask, jsonify
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

app = Flask(__name__)

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='uo0ixnhgo28j14zodvyvu7evfymk3ekzfgach2c2lqhb1yoi')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('gpttest-main.bnuu11xasp.viam.cloud', opts)

async def drive_forward(base):
    # Moves the Viam Rover forward 500mm at 500mm/s
    await base.move_straight(velocity=500, distance=500)
    print("Rover moved forward")

@app.route('/drive_forward', methods=['POST'])
def api_drive_forward():
    robot = asyncio.run(connect())
    rover_base = Base.from_robot(robot, 'viam_base')
    asyncio.run(drive_forward(rover_base))
    asyncio.run(robot.close())

    response = {
        "status": "success",
        "message": "Rover moved forward"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()

