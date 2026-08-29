def translate(data):
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")
    required_fields = ['action', 'pull_request', 'repository']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    pull_request = data['pull_request']
    repository = data['repository']
    required_pr_fields = ['number', 'title', 'user', 'head', 'base', 'created_at', 'html_url', 'draft']
    for field in required_pr_fields:
        if field not in pull_request:
            raise ValueError(f"Missing required field in pull_request: {field}")
    if data['action'] not in ['opened', 'closed', 'reopened', 'synchronize']:
        raise ValueError(f"Invalid action: {data['action']}")
    pr_user = pull_request['user']
    pr_head = pull_request['head']
    pr_base = pull_request['base']
    for obj, field, label in ((pr_user, 'login', 'user'), (pr_head, 'ref', 'head'), (pr_base, 'ref', 'base')):
        if not isinstance(obj, dict) or field not in obj:
            raise ValueError(f"Missing required field in {label}: {field}")
    return {
        'event_type': data['action'],
        'pr_number': pull_request['number'],
        'title': pull_request['title'],
        'description': pull_request.get('body', None),
        'author_login': pr_user['login'],
        'source_branch': pr_head['ref'],
        'target_branch': pr_base['ref'],
        'repo_full_name': repository['full_name'],
        'draft': pull_request['draft'],
        'created_at': pull_request['created_at'],
        'url': pull_request['html_url'],
        'labels': [label['name'] for label in pull_request.get('labels', [])],
        'reviewers': [reviewer['login'] for reviewer in pull_request.get('requested_reviewers', [])]
    }
