# nothing-but-a-rank
Literally, nothing but a rank.  
**For secondary changes/releases, please credit the original author and modifier.**

**Original Author: 0x24a  
Modifier: lightworld689**

## Features
- Increment user click count.
- Retrieve user rank based on click count.
- Rate limiting to prevent abuse.
- Read-only endpoint to get total clicks.
- Endpoint to get top 10 users and total clicks.

## API Endpoints
- `GET /{username}`: Increment user's click count and return the count and rank.
- `GET /readonly`: Get total clicks without modifying any data.
- `GET /`: Get top 10 users and total clicks.

## Install
Just like you install any other Python project on GitHub.
```bash
$ git clone https://github.com/lightworld689/nothing-but-a-rank.git
$ cd nothing-but-a-rank
$ python3 -m pip3 install -r requirements.txt
```

## Run
Run it with any ASGI server you like.
For example, Uvicorn:
```
$ uvicorn main:app
```
