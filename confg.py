from flask import Flask, render_template,request,flash,redirect,url_for,session,logging,jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_pymongo import pymongo
from datetime import datetime
from bson import ObjectId
import logging
import sys
import dns
import os


CONNECTION_STRING = 'mongodb+srv://kopf:1234567890@cluster0.jhodt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
DATABASE_NAME = 'myFirstDatabase'
