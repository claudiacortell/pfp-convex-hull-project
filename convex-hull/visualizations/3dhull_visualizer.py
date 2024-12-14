# import subprocess
# import json
# import os
# import re
# import webbrowser
# import random
# from datetime import datetime

# def run_convex_hull_algorithm(num_points):
#     """
#     Run the convex hull algorithm and capture its output.
    
#     Args:
#         num_points (int): Number of points to generate
    
#     Returns:
#         tuple: List of all points, list of hull vertices
#     """
#     command = f"stack exec convex-hull-exe -- {num_points} quickHullPar 3d"
    
#     try:
#         result = subprocess.run(command, shell=True, capture_output=True, text=True)
#         output = result.stdout
#     except Exception as e:
#         print(f"Error running convex hull algorithm: {e}")
#         return None, None
    
#     all_points_match = re.findall(r'V3 ([\d.-]+) ([\d.-]+) ([\d.-]+)', output)
#     all_points = [list(map(float, point)) for point in all_points_match]
#     hull_match = re.findall(r'V3 ([\d.-]+) ([\d.-]+) ([\d.-]+)', output.split('Found')[1].split(']')[0])
#     hull_vertices = [list(map(float, vertex)) for vertex in hull_match]
#     return all_points, hull_vertices

# def generate_html_visualizer(all_points, hull_vertices, num_points):
#     """
#     Generate an HTML file with a 3D Convex Hull visualization.
#     Args:
#         all_points (list): List of all generated points
#         hull_vertices (list): List of convex hull vertices
#         num_points (int): Number of points generated
#     """
#     html_template = f"""<!DOCTYPE html>
# <html>
# <head>
#     <title>3D Convex Hull Visualization</title>
#     <style>
#         html, body {{
#             height: 100%;
#             margin: 0;
#             padding: 0;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             background-color: #f0f0f0;
#             font-family: Arial, sans-serif;
#         }}
#         .container {{
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             width: 100%;
#             max-width: 600px;
#         }}
#         canvas {{
#             border: 1px solid #ccc;
#             border-radius: 8px;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             background-color: white;
#             margin-bottom: 20px;
#         }}
#         .legend {{
#             display: flex;
#             align-items: center;
#             gap: 20px;
#             margin-bottom: 10px;
#         }}
#         .legend-item {{
#             display: flex;
#             align-items: center;
#             gap: 8px;
#         }}
#         .legend-dot {{
#             width: 12px;
#             height: 12px;
#             border-radius: 50%;
#         }}
#         .red-dot {{ background-color: red; }}
#         .blue-dot {{ background-color: blue; }}
#         .info {{
#             font-size: 14px;
#             color: #666;
#         }}
#     </style>
# </head>
# <body>
#     <div class="container">
#         <canvas id="canvas" width="600" height="450"></canvas>
#         <div class="legend">
#             <div class="legend-item">
#                 <div class="legend-dot red-dot"></div>
#                 <span>Hull Vertices</span>
#             </div>
#             <div class="legend-item">
#                 <div class="legend-dot blue-dot"></div>
#                 <span>Internal Points</span>
#             </div>
#         </div>
#         <div class="info">
#             Total Points: {num_points} | Hull Vertices: {len(hull_vertices)}
#         </div>
#     </div>

#     <script>
#         // All points
#         const allPoints = {json.dumps(all_points)};

#         // Hull vertices
#         const hullVertices = {json.dumps(hull_vertices)};

#         // Generate triangular faces
#         const faces = [];
#         for (let i = 0; i < hullVertices.length - 2; i++) {{
#             for (let j = i + 1; j < hullVertices.length - 1; j++) {{
#                 for (let k = j + 1; k < hullVertices.length; k++) {{
#                     faces.push([i, j, k]);
#                 }}
#             }}
#         }}

#         const canvas = document.getElementById('canvas');
#         const ctx = canvas.getContext('2d');
#         let rotation = 0;

#         // Normalize points to fit within a unit cube
#         function normalizePoints(points) {{
#             // Find min and max for each dimension
#             const mins = [
#                 Math.min(...points.map(p => p[0])),
#                 Math.min(...points.map(p => p[1])),
#                 Math.min(...points.map(p => p[2]))
#             ];
#             const maxs = [
#                 Math.max(...points.map(p => p[0])),
#                 Math.max(...points.map(p => p[1])),
#                 Math.max(...points.map(p => p[2]))
#             ];

#             // Calculate scale factors
#             const scales = maxs.map((max, i) => max - mins[i] || 1);
#             const maxScale = Math.max(...scales);

#             return points.map(point => 
#                 point.map((coord, i) => (coord - mins[i]) / maxScale * 2 - 1)
#             );
#         }}

#         // Normalize points
#         const normalizedAllPoints = normalizePoints([...allPoints, ...hullVertices]);
#         const normalizedPoints = normalizedAllPoints.slice(0, allPoints.length);
#         const normalizedHull = normalizedAllPoints.slice(allPoints.length);

#         // Project 3D point to 2D
#         function project(point, rotation) {{
#             const scale = 250;
#             const [x, y, z] = point;
            
#             // Rotate around Y axis
#             const rotatedX = x * Math.cos(rotation) - z * Math.sin(rotation);
#             const rotatedZ = x * Math.sin(rotation) + z * Math.cos(rotation);
            
#             // Simple perspective projection
#             const distance = 3;
#             const perspective = distance / (distance + rotatedZ + 1);
            
#             return {{
#                 x: (rotatedX * perspective * scale) + 300,
#                 y: (y * perspective * scale) + 400, 
#                 z: rotatedZ
#             }};
#         }}

#         function calculateFaceDepth(face, projectedPoints) {{
#             const [i, j, k] = face;
#             return (projectedPoints[i].z + projectedPoints[j].z + projectedPoints[k].z) / 3;
#         }}

#         function draw() {{
#             ctx.clearRect(0, 0, canvas.width, canvas.height);

#             // Draw background grid
#             ctx.strokeStyle = '#eee';
#             ctx.lineWidth = 1;
#             for (let i = 0; i < canvas.width; i += 50) {{
#                 ctx.beginPath();
#                 ctx.moveTo(i, 0);
#                 ctx.lineTo(i, canvas.height);
#                 ctx.stroke();
#                 ctx.beginPath();
#                 ctx.moveTo(0, i);
#                 ctx.lineTo(canvas.width, i);
#                 ctx.stroke();
#             }}

#             // Project all points
#             const projectedHull = normalizedHull.map(p => project(p, rotation));
#             const projectedInternal = normalizedPoints.map(p => project(p, rotation));

#             // Sort faces by depth
#             const facesWithDepth = faces.map(face => ({{
#                 faceIndices: face,
#                 depth: calculateFaceDepth(face, projectedHull)
#             }}));
#             facesWithDepth.sort((a, b) => a.depth - b.depth);

#             // Draw faces with transparency
#             ctx.globalAlpha = 0.2;
#             facesWithDepth.forEach((faceData) => {{
#                 const [i, j, k] = faceData.faceIndices;
#                 ctx.beginPath();
#                 ctx.moveTo(projectedHull[i].x, projectedHull[i].y);
#                 ctx.lineTo(projectedHull[j].x, projectedHull[j].y);
#                 ctx.lineTo(projectedHull[k].x, projectedHull[k].y);
#                 ctx.closePath();
#                 ctx.fillStyle = '#ff6666';
#                 ctx.fill();
#             }});
#             ctx.globalAlpha = 1.0;

#             // Draw hull edges
#             ctx.strokeStyle = '#ff0000';
#             ctx.lineWidth = 2;
#             for (let i = 0; i < projectedHull.length; i++) {{
#                 for (let j = i + 1; j < projectedHull.length; j++) {{
#                     const p1 = projectedHull[i];
#                     const p2 = projectedHull[j];
#                     ctx.beginPath();
#                     ctx.moveTo(p1.x, p1.y);
#                     ctx.lineTo(p2.x, p2.y);
#                     ctx.stroke();
#                 }}
#             }}

#             // Draw hull vertices
#             ctx.fillStyle = '#ff0000';
#             projectedHull.forEach(p => {{
#                 ctx.beginPath();
#                 ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
#                 ctx.fill();
#             }});

#             // Draw internal points with smaller size
#             ctx.fillStyle = '#0000ff';
#             projectedInternal.forEach(p => {{
#                 ctx.beginPath();
#                 ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
#                 ctx.fill();
#             }});

#             // Update rotation
#             rotation = (rotation + 0.01) % (Math.PI * 2);
#             requestAnimationFrame(draw);
#         }}

#         // Start animation
#         draw();
#     </script>
# </body>
# </html>"""
    
#     os.makedirs('convex_hull_visualizations', exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f'convex_hull_visualizations/convex_hull_viz_{timestamp}.html'
#     with open(filename, 'w') as f:
#         f.write(html_template)
#     print(f"Visualization saved to {filename}")
#     return filename

# def main():
#     num_points = random.randint(10, 100)
#     all_points, hull_vertices = run_convex_hull_algorithm(num_points)
#     if all_points and hull_vertices:
#         generated_file = generate_html_visualizer(all_points, hull_vertices, num_points)
#         webbrowser.open('file://' + os.path.realpath(generated_file))

# if __name__ == "__main__":
#     main()

import subprocess
import json
import os
import re
import webbrowser
import random
from datetime import datetime

def run_convex_hull_algorithm(num_points):
    """
    Run the convex hull algorithm and capture its output.
    
    Args:
        num_points (int): Number of points to generate
    
    Returns:
        tuple: List of all points, list of hull vertices
    """
    command = f"stack exec convex-hull-exe -- {num_points} quickHullPar 3d"
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        print(f"Error running convex hull algorithm: {e}")
        return None, None
    
    all_points_match = re.findall(r'V3 ([\d.-]+) ([\d.-]+) ([\d.-]+)', output)
    all_points = [list(map(float, point)) for point in all_points_match]
    hull_match = re.findall(r'V3 ([\d.-]+) ([\d.-]+) ([\d.-]+)', output.split('Found')[1].split(']')[0])
    hull_vertices = [list(map(float, vertex)) for vertex in hull_match]
    return all_points, hull_vertices

def generate_html_visualizer(all_points, hull_vertices, num_points):
    """
    Generate an HTML file with a 3D Convex Hull visualization.
    Args:
        all_points (list): List of all generated points
        hull_vertices (list): List of convex hull vertices
        num_points (int): Number of points generated
    """
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>3D Convex Hull Visualization (Improved)</title>
    <style>
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            max-width: 600px;
        }
        canvas {
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            background-color: white;
            margin-bottom: 20px;
        }
        .legend {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-shape {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .circle {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: rgba(255, 0, 0, 0.4);
        }
        .square {
            width: 10px;
            height: 10px;
            background-color: blue;
            transform: rotate(45deg);
        }
        .info {
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <canvas id="canvas" width="600" height="450"></canvas>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-shape"><div class="circle"></div></div>
                <span>Hull Vertices</span>
            </div>
            <div class="legend-item">
                <div class="legend-shape"><div class="square"></div></div>
                <span>Internal Points</span>
            </div>
        </div>
        <div class="info">
            Total Points: ''' + str(num_points) + ''' | Hull Vertices: ''' + str(len(hull_vertices)) + '''
        </div>
    </div>

    <script>
        // All points and hull vertices
        const allPoints = ''' + json.dumps(all_points) + ''';
        const hullVertices = ''' + json.dumps(hull_vertices) + ''';

        // Generate triangular faces
        const faces = [];
        for (let i = 0; i < hullVertices.length - 2; i++) {
            for (let j = i + 1; j < hullVertices.length - 1; j++) {
                for (let k = j + 1; k < hullVertices.length; k++) {
                    faces.push([i, j, k]);
                }
            }
        }

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let rotation = 0;

        function normalizePoints(points) {
            const mins = [
                Math.min(...points.map(p => p[0])),
                Math.min(...points.map(p => p[1])),
                Math.min(...points.map(p => p[2]))
            ];
            const maxs = [
                Math.max(...points.map(p => p[0])),
                Math.max(...points.map(p => p[1])),
                Math.max(...points.map(p => p[2]))
            ];

            const scales = maxs.map((max, i) => max - mins[i] || 1);
            const maxScale = Math.max(...scales);

            return points.map(point => 
                point.map((coord, i) => (coord - mins[i]) / maxScale * 2 - 1)
            );
        }

        const normalizedAllPoints = normalizePoints([...allPoints, ...hullVertices]);
        const normalizedPoints = normalizedAllPoints.slice(0, allPoints.length);
        const normalizedHull = normalizedAllPoints.slice(allPoints.length);

        function project(point, rotation) {
            const scale = 250;
            const [x, y, z] = point;
            
            const rotatedX = x * Math.cos(rotation) - z * Math.sin(rotation);
            const rotatedZ = x * Math.sin(rotation) + z * Math.cos(rotation);
            
            const distance = 3;
            const perspective = distance / (distance + rotatedZ + 1);
            
            return {
                x: (rotatedX * perspective * scale) + 300,
                y: (y * perspective * scale) + 400, 
                z: rotatedZ
            };
        }

        function calculateFaceDepth(face, projectedPoints) {
            const [i, j, k] = face;
            return (projectedPoints[i].z + projectedPoints[j].z + projectedPoints[k].z) / 3;
        }

        function drawSquare(ctx, x, y, size) {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(Math.PI / 4); // 45-degree rotation
            ctx.fillRect(-size/2, -size/2, size, size);
            ctx.restore();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw background grid
            ctx.strokeStyle = '#eee';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }

            const projectedHull = normalizedHull.map(p => project(p, rotation));
            const projectedInternal = normalizedPoints.map(p => project(p, rotation));

            // Sort faces by depth
            const facesWithDepth = faces.map(face => ({
                faceIndices: face,
                depth: calculateFaceDepth(face, projectedHull)
            }));
            facesWithDepth.sort((a, b) => a.depth - b.depth);

            // Draw faces with increased transparency
            ctx.globalAlpha = 0.08;  // Made more transparent
            facesWithDepth.forEach((faceData) => {
                const [i, j, k] = faceData.faceIndices;
                ctx.beginPath();
                ctx.moveTo(projectedHull[i].x, projectedHull[i].y);
                ctx.lineTo(projectedHull[j].x, projectedHull[j].y);
                ctx.lineTo(projectedHull[k].x, projectedHull[k].y);
                ctx.closePath();
                ctx.fillStyle = '#ff6666';
                ctx.fill();
            });

            // Draw hull edges with transparency
            ctx.globalAlpha = 0.04;  // Made more transparent
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 2;
            for (let i = 0; i < projectedHull.length; i++) {
                for (let j = i + 1; j < projectedHull.length; j++) {
                    const p1 = projectedHull[i];
                    const p2 = projectedHull[j];
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }

            // Draw internal points as rotated squares with depth-based size
            ctx.globalAlpha = 0.8;
            ctx.fillStyle = '#0000ff';
            projectedInternal.forEach(p => {
                const baseSize = 12;
                const sizeModifier = (p.z + 1) / 2;
                const size = baseSize * sizeModifier;
                drawSquare(ctx, p.x, p.y, size);
            });

            // Draw hull vertices as more transparent circles
            ctx.globalAlpha = 0.4;  // Made more transparent
            ctx.fillStyle = '#ff0000';
            projectedHull.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
                ctx.fill();
            });

            rotation = (rotation + 0.01) % (Math.PI * 2);
            requestAnimationFrame(draw);
        }

        draw();
    </script>
</body>
</html>'''
    
    os.makedirs('convex_hull_visualizations', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'convex_hull_visualizations/convex_hull_viz_{timestamp}.html'
    with open(filename, 'w') as f:
        f.write(html_template)
    print(f"Visualization saved to {filename}")
    return filename

def main():
    num_points = random.randint(10, 100)
    all_points, hull_vertices = run_convex_hull_algorithm(num_points)
    if all_points and hull_vertices:
        generated_file = generate_html_visualizer(all_points, hull_vertices, num_points)
        webbrowser.open('file://' + os.path.realpath(generated_file))

if __name__ == "__main__":
    main()