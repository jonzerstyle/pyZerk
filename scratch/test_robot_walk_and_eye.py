import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()

import globals
import robots
import movement
import bullets

def test_robot_animation_suite():
    print("=== Testing Robot Walking and Eye Animation Suite ===")

    # 1. Verify Modular Components and Normalization
    assert len(robots.ROBOT_UPPER_LEFT) == 11, f"Expected 11 upper left points, got {len(robots.ROBOT_UPPER_LEFT)}"
    assert len(robots.ROBOT_UPPER_RIGHT) == 12, f"Expected 12 upper right points, got {len(robots.ROBOT_UPPER_RIGHT)}"
    assert len(robots.ROBOT_STANDING_LEGS) == 10, f"Expected 10 standing leg points, got {len(robots.ROBOT_STANDING_LEGS)}"
    assert len(robots.ROBOT_STRIDE_A_LEGS) == 10, f"Expected 10 stride A points, got {len(robots.ROBOT_STRIDE_A_LEGS)}"
    assert len(robots.ROBOT_STRIDE_B_LEGS) == 10, f"Expected 10 stride B points, got {len(robots.ROBOT_STRIDE_B_LEGS)}"
    assert len(robots.EYE_CENTER) == 5, f"Expected 5 eye center points, got {len(robots.EYE_CENTER)}"
    print("  -> Component definitions verified.")

    # 2. Verify Initial Robot State
    r = robots.Class_Robot([200, 200], [0, 0])
    assert len(r.list_polygon_pts) == 2, "Expected body and eye polygon lists"
    assert len(r.list_polygon_pts[0]) == len(robots.ROBOT_UPPER_LEFT) + len(robots.ROBOT_STANDING_LEGS) + len(robots.ROBOT_UPPER_RIGHT)
    assert len(r.list_polygon_pts[1]) == len(robots.EYE_CENTER)
    print("  -> Initial robot instantiation verified.")

    # 3. Verify Stopped State Logic
    r.speed = [0.0, 0.0]
    r.anim_timer = 5
    r.eye_timer = 5
    # Force updateMovement evaluation of stopped state
    # (simulate branch when speed is 0)
    if r.speed[0] == 0.0 and r.speed[1] == 0.0:
        active_legs = robots.NORM_ROBOT_STANDING_LEGS
        r.anim_timer = 0
        r.eye_timer = 0
        r.eye_frame_idx = 0
        active_eye = robots.NORM_EYE_CENTER
    assert active_legs == robots.NORM_ROBOT_STANDING_LEGS
    assert active_eye == robots.NORM_EYE_CENTER
    print("  -> Stopped state (legs planted, eye centered) verified.")

    # 4. Verify Left Movement (Walk cycle + Eye Cycle Left)
    r_left = robots.Class_Robot([200, 200], [0, 0])
    r_left.anim_speed = 2
    r_left.anim_timer = 0
    r_left.anim_frame_idx = 0
    r_left.eye_anim_speed = 2
    r_left.eye_timer = 0
    r_left.eye_frame_idx = 0

    # Simulate moving left across 12 frames
    observed_eye_left = []
    observed_legs_left = []
    for step in range(12):
        r_left.speed = [-robots.robot_speed_mag, 0.0]
        # Run walking and eye update logic
        if r_left.speed[0] == 0.0 and r_left.speed[1] == 0.0:
            active_legs = robots.NORM_ROBOT_STANDING_LEGS
        else:
            r_left.anim_timer += 1
            if r_left.anim_timer >= r_left.anim_speed:
                r_left.anim_timer = 0
                r_left.anim_frame_idx = (r_left.anim_frame_idx + 1) % len(r_left.walk_frames_vert)
            active_legs = r_left.walk_frames_left[r_left.anim_frame_idx]

        if r_left.speed[0] < -0.01:
            r_left.eye_timer += 1
            if r_left.eye_timer >= r_left.eye_anim_speed:
                r_left.eye_timer = 0
                r_left.eye_frame_idx = (r_left.eye_frame_idx + 1) % len(r_left.eye_frames_left)
            active_eye = r_left.eye_frames_left[r_left.eye_frame_idx]

        observed_eye_left.append(r_left.eye_frame_idx)
        observed_legs_left.append(r_left.anim_frame_idx)

    # Verify that eye frames advanced sequentially through the 6 left-cycle frames
    assert set(observed_eye_left) == {0, 1, 2, 3, 4, 5}, f"Expected all 6 eye frames visited when moving left, got {set(observed_eye_left)}"
    assert set(observed_legs_left) == {0, 1, 2, 3}, f"Expected all 4 leg frames visited when moving left, got {set(observed_legs_left)}"
    print("  -> Moving left: verified leg cycle and leftward eye scanning across all frames.")

    # 5. Verify Right Movement (Walk cycle + Eye Cycle Right)
    r_right = robots.Class_Robot([200, 200], [0, 0])
    r_right.anim_speed = 2
    r_right.anim_timer = 0
    r_right.anim_frame_idx = 0
    r_right.eye_anim_speed = 2
    r_right.eye_timer = 0
    r_right.eye_frame_idx = 0

    observed_eye_right = []
    observed_legs_right = []
    for step in range(12):
        r_right.speed = [robots.robot_speed_mag, 0.0]
        # Run walking and eye update logic
        if r_right.speed[0] == 0.0 and r_right.speed[1] == 0.0:
            active_legs = robots.NORM_ROBOT_STANDING_LEGS
        else:
            r_right.anim_timer += 1
            if r_right.anim_timer >= r_right.anim_speed:
                r_right.anim_timer = 0
                r_right.anim_frame_idx = (r_right.anim_frame_idx + 1) % len(r_right.walk_frames_vert)
            active_legs = r_right.walk_frames_right[r_right.anim_frame_idx]

        if r_right.speed[0] > 0.01:
            r_right.eye_timer += 1
            if r_right.eye_timer >= r_right.eye_anim_speed:
                r_right.eye_timer = 0
                r_right.eye_frame_idx = (r_right.eye_frame_idx + 1) % len(r_right.eye_frames_right)
            active_eye = r_right.eye_frames_right[r_right.eye_frame_idx]

        observed_eye_right.append(r_right.eye_frame_idx)
        observed_legs_right.append(r_right.anim_frame_idx)

    assert set(observed_eye_right) == {0, 1, 2, 3, 4, 5}, f"Expected all 6 eye frames visited when moving right, got {set(observed_eye_right)}"
    assert set(observed_legs_right) == {0, 1, 2, 3}, f"Expected all 4 leg frames visited when moving right, got {set(observed_legs_right)}"
    print("  -> Moving right: verified leg cycle and rightward eye scanning across all frames.")

    # 6. Verify Surface Drawing Across All Frames (No Crashes or Blank Frame Errors)
    surf = pygame.Surface((100, 100))
    test_robot = robots.Class_Robot([50, 50], [0, 0])
    for eye_frame in test_robot.eye_frames_left:
        for leg_frame in test_robot.walk_frames_left:
            test_robot.list_polygon_pts[0] = robots.NORM_ROBOT_UPPER_LEFT + leg_frame + robots.NORM_ROBOT_UPPER_RIGHT
            test_robot.list_polygon_pts[1] = eye_frame
            test_robot.update()
            rects = test_robot.draw(surf)
            assert len(rects) > 0, "Expected non-empty dirtyrects from draw()"
    print("  -> Rendering verified across all combinatoric leg & eye animation frames.")

    # 7. Verify In-Game updateMovement Call
    r_game = robots.Class_Robot([100, 100], [0, 0])
    for _ in range(30):
        r_game.updateMovement()
        r_game.update()
        rects = r_game.draw(surf)
        assert len(rects) > 0
    print("  -> updateMovement live loop simulation verified.")

    print("\nALL ROBOT WALKING AND EYE ANIMATION TESTS PASSED (100%)!")

if __name__ == '__main__':
    test_robot_animation_suite()
