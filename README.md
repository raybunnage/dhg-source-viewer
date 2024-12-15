# dhg-source-viewer

A Streamlit-powered web application for viewing DHG shared folders and files, integrated with Supabase for data storage and authentication.

## Features

- View shared folders and files
- Authentication using Supabase
- Easy navigation through folder structure
- File preview capabilities
- Secure access control

## Setup

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

3. Run locally:
```bash
streamlit run app.py
```

## Project Structure

```
dhg-source-viewer/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py
└── src/
    ├── __init__.py
    ├── auth.py
    ├── database.py
    └── utils.py
```

## Deployment

This application is deployed on Streamlit Cloud. Visit [app url] to see it in action.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request