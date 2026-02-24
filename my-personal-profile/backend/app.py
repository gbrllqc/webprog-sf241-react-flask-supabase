import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client

# Initialize Flask with the path to the React build (Vite uses 'dist')
app = Flask(__name__, 
            static_folder='../frontend/dist', 
            static_url_path='/')

# Allow CORS for local development (important if React/Flask are on different ports)
CORS(app) 

# Supabase Credentials from Environment Variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- API ROUTES ---
# Keep your /guestbook prefix so the frontend knows how to find them
@app.route('/api/guestbook', methods=['GET'])
def get_entries():
    response = supabase.table("guestbook").select("*").order("created_at", desc=True).execute()
    return jsonify(response.data)

@app.route('/api/guestbook', methods=['POST'])
def add_entry():
    data = request.json
    response = supabase.table("guestbook").insert(data).execute()
    return jsonify(response.data), 201

@app.route('/api/guestbook/<id>', methods=['PUT'])
def update_entry(id):
    data = request.json
    response = supabase.table("guestbook").update(data).eq("id", id).execute()
    return jsonify(response.data)

@app.route('/api/guestbook/<id>', methods=['DELETE'])
def delete_entry(id):
    supabase.table("guestbook").delete().eq("id", id).execute()
    return jsonify({"message": "Deleted successfully"}), 200

# --- STATIC FILE SERVING & CATCH-ALL ROUTE ---
# This is what fixes the "Not Found" error on Render
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Check if the requested file exists in the frontend dist folder
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # If the file doesn't exist, serve the React index.html
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)