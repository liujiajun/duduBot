from google.oauth2 import service_account
import dialogflow_v2 as dialogflow
import json


class DialogflowClient:
    def __init__(self):
        with open('bot_config_private.json') as f:  # Use bot_config_private.json for development
            config = json.load(f)
        self.credential = service_account.Credentials.from_service_account_file(config['dialogflow_credential_path'])
        self.sessionClient = dialogflow.SessionsClient(credentials=self.credential)
        self.projectId = config['dialogflow_project_id']

    def detectIntent(self, sessionId, text, languageCode='en-US'):
        session = self.sessionClient.session_path(self.projectId, sessionId)
        print('Session path: {}\n'.format(session))

        text_input = dialogflow.types.TextInput(text=text, language_code=languageCode)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = self.sessionClient.detect_intent(session=session, query_input=query_input)

        return response.query_result.fulfillment_text

