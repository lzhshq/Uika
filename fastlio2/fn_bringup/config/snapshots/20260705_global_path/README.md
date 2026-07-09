# Uika Global Path Snapshot

Saved on 2026-07-05 after interactive RViz tuning.

This snapshot freezes the current obstacle-course global route and terrain zones
before adding the mission executor layer.

Files:

- `uika_obstacle_mission_stair_frame.yaml`: ordered obstacle route, entry/exit
  points, required points, Bezier route segments, and per-obstacle policy names.
- `uika_terrain_zones_stair_frame.yaml`: terrain zone polygons used for
  visualization, path segmentation, and policy context.

Coordinate convention:

- `frame_id: map`
- Origin: top center of the T-stair platform.
- `+x`: toward the high-wall side.
- `+y`: toward the big-slope side.
- Main ground is approximately `z=-0.4`; stair-top origin is `z=0`.

Current obstacle order:

1. `start_down_stairs`
2. `high_wall`
3. `pole_slalom`
4. `gravel_wood_pit`
5. `low_bar`
6. `big_slope`
7. `bridge_b`
8. `bridge_a`
9. `t_stairs`
