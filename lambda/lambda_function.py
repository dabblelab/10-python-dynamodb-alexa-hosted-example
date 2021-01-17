"""
 Copyright (C) 2020 Dabble Lab - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 
 For additional copyright information please
 visit : http://dabblelab.com/copyright
 """

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

import logging
import json
import random
import os
import boto3


# Defining the database region, table name and dynamodb persistence adapter
ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)

# Initializing the logger and setting the level to "INFO"
# Read more about it here https://www.loggly.com/ultimate-guide/python-logging-basics/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Intent Handlers

# This Handler is called when the skill is invoked by using only the invocation name(Ex. Alexa, open template ten)
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        skill_name = language_prompts["SKILL_NAME"]
        
        try:
            # Fetch user's name from the DB.
            user_name = persistent_attributes['user_name']
            speech_output = random.choice(language_prompts["REPEAT_USER_GREETING"]).format(user_name)
            reprompt = random.choice(language_prompts["REPEAT_USER_GREETING_REPROMPT"])
        except:
            speech_output = random.choice(language_prompts["FIRST_TIME_USER"]).format(skill_name)
            reprompt = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class MyNameIsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MyNameIsIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        user_name = handler_input.request_envelope.request.intent.slots["UserNameSlot"].value
        persistent_attributes["user_name"] = user_name
        
        # Write user's name to the DB.
        handler_input.attributes_manager.save_persistent_attributes()
        
        speech_output = random.choice(language_prompts["NAME_SAVED"]).format(user_name)
        reprompt = random.choice(language_prompts["NAME_SAVED_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class WhatsMyNameIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("WhatsMyNameIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        try:
            # Read user's name from the DB.
            user_name = persistent_attributes['user_name']
            
            speech_output = random.choice(language_prompts["TELL_NAME"]).format(user_name)
            reprompt = random.choice(language_prompts["TELL_NAME_REPROMPT"])
        except:
            speech_output = random.choice(language_prompts["NO_NAME"])
            reprompt = random.choice(language_prompts["NO_NAME_REPROMPT"])        
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class UpdateNameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("UpdateNameIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        user_name = handler_input.request_envelope.request.intent.slots["NewNameSlot"].value
        # Update user's name
        persistent_attributes["user_name"] = user_name
        handler_input.attributes_manager.save_persistent_attributes()
        
        speech_output = random.choice(language_prompts["NAME_UPDATED"]).format(user_name)
        reprompt = random.choice(language_prompts["NAME_UPDATED_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class DeleteNameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteNameIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        # Delete all attributes from the DB
        handler_input.attributes_manager.delete_persistent_attributes()
        
        speech_output = random.choice(language_prompts["NAME_DELETED"])
        reprompt = random.choice(language_prompts["NAME_DELETED_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        repeat_speech_output = session_attributes["repeat_speech_output"]
        repeat_reprompt = session_attributes["repeat_reprompt"]
        
        speech_output = random.choice(language_prompts["REPEAT"]).format(repeat_speech_output)
        reprompt = random.choice(language_prompts["REPEAT_REPROMPT"]).format(repeat_reprompt)
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handlers

# This exception handler handles syntax or routing errors. If you receive an error stating 
# the request handler is not found, you have not implemented a handler for the intent or 
# included it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# Interceptors

# This interceptor logs each request sent from Alexa to our endpoint.
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

# This interceptor logs each response our endpoint sends back to Alexa.
class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

# This interceptor fetches the speech_output and reprompt messages from the response and pass them as
# session attributes to be used by the repeat intent handler later on.
class RepeatInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        try:
            session_attributes["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        except:
            session_attributes["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")


# Skill Builder
# Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(MyNameIsIntentHandler())
sb.add_request_handler(WhatsMyNameIntentHandler())
sb.add_request_handler(UpdateNameIntentHandler())
sb.add_request_handler(DeleteNameIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()