# Streamlit Application Documentation

## Overview
The Streamlit application serves as a web interface for managing and displaying various services including Supabase authentication, Google Drive integration, and Anthropic AI interactions.

## Main Components

### Page Configuration
- Title: "DHG Source Viewer"
- Icon: 📁
- Layout: Wide format
- Sidebar: Expanded by default

### Navigation
The application features a sidebar navigation with three main sections:
- Supabase Management
- Privacy Policy
- Terms of Service

### Features

#### 1. Supabase Management
```python
show_supabase_management()
```
- Connects to Supabase database
- Displays user count and todo items
- Includes authentication interface
- Integrates with video display and Anthropic AI testing

#### 2. Supabase Authentication
```python
show_supabase_auth()
```
- Provides user signup/login functionality
- Email and password input fields
- Handles authentication responses
- Displays success/error messages

#### 3. Google Drive Integration
```python
show_first_mp4_video()
```
- Authenticates with Google Drive
- Lists and displays MP4 files
- Streams video content via iframe
- Handles errors gracefully

#### 4. Anthropic AI Integration
```python
show_anthropic_test()
```
- Connects to Anthropic API
- Performs basic and complex tests
- Handles follow-up responses

#### 5. Documentation Pages
```python
show_privacy_policy()
show_terms_of_service()
```
- Displays privacy policy from markdown file
- Displays terms of service from markdown file

## Configuration

### Required Environment Variables
The application requires the following secrets:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `TEST_EMAIL`
- `TEST_PASSWORD`
- `ANTHROPIC_API_KEY`
- `PRIVATE_KEY`
- `PRIVATE_KEY_ID`
- `CLIENT_EMAIL`
- `CLIENT_ID`

### Running the Application
To run the application:
```bash
streamlit run streamlit_app.py
```

## Security Features
- Secure password input handling
- Environment variable management through Streamlit secrets
- Safe HTML rendering with `unsafe_allow_html` parameter

## UI Components
- Custom CSS for maximum width (1200px)
- Responsive layout
- Google site verification meta tag
- Centered footer with copyright information

## Error Handling
- Graceful error handling for file operations
- User feedback for authentication processes
- Service connection error management
