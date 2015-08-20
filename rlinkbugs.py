#!/usr/bin/env python
# -!- coding: utf8 -!-

bugsdir='bugs'
newreports='new_reports.txt'
newbugs='new_bugs.txt'

types = {
  'bug': u'Bug',
  'improvement': u'Amélioration'
}

categories = {
  'nav': u'Navigation / GPS',
  'myzeonline': u'My Z.E. Online, services en ligne et applications Renault',
  'apps': u'Applications tierces',
  'voice': u'Reconnaissance vocale, téléphone, etc.',
  'counter': u'Compteurs et bilan trajet',
  'multimedia': u'Multimédia',
  'unclassified': u'Non classé'
}

###########################################################################

import codecs
import os

from flask import Flask, render_template, request

from markdown import Markdown

###########################################################################

def get_bug(filename):
    print 'Getting for {}'.format(filename)
    if filename[-4:] != '.txt':
         filename = filename + '.txt'
    with codecs.open(os.path.join(bugsdir, filename), 'r', 'utf-8-sig') as f:
        text = f.read()
    md = Markdown(extensions=['markdown.extensions.meta'],
                  output_format='html5')
    output={'content':md.convert(text)}
    output['title'] = md.Meta.get('title', [''])[0]
    output['id'] = filename[:-4]
    output['type'] = types.get(md.Meta.get('type', ['bug'])[0], 'bug')
    output['category'] = categories.get(md.Meta.get('category', ['unclassified'])[0], 'unclassified')
    output['validators'] = []
    output['working'] = []
    for experience in md.Meta.get('xp', ['']):
        splitted = experience.split(',')
        name = splitted[0]
        email = splitted[1]
        verified = splitted[2]
        data = {
            'name': name,
        }
        for elem in splitted[3:]:
            splitelem = elem.split('=')
            data[splitelem[0]] = splitelem[1]
        if verified == 'yes':
            output['validators'].append(data)
        elif verified == 'no':
            output['working'].append(data)
    return output

def list_bugs():
    lst = []
    for filename in os.listdir(bugsdir):
        if filename[-4:] == '.txt':
            lst.append(get_bug(filename))
    return lst

###########################################################################

app = Flask(__name__)
#app.debug = True

@app.route('/')
def root():
    return render_template('home.html')

@app.route('/rlink')
def rlink():
    return render_template('rlink.html')

@app.route('/bugs', methods=['GET', 'POST'])
@app.route('/bugs/', methods=['GET', 'POST'])
def bugs():
    if request.method == 'POST':
        frm = request.form
        with open(newbugs, 'a') as f:
            f.write(
               'description={}|name={}|email={}|car={}|version={}\n'.format(
                   frm['description'].encode('utf8'), frm['name'].encode('utf8'), frm['email'].encode('utf8'), frm['car'].encode('utf8'), frm['version'].encode('utf8')
               )
            )
        newbug = True
    else:
        newbug = False
    return render_template('bugs.html', bugs=list_bugs(), newbug=newbug)

@app.route('/bugs/<bid>', methods=['GET', 'POST'])
def bug(bid):
    if request.method == 'POST':
        frm = request.form
        with open(newreports, 'a') as f:
            f.write(
               'bug_id={}|i_have_the_bug={}|name={}|email={}|'
               'car={}|version={}|comment={}\n'.format(
                   bid, frm['verif'].encode('utf8'), frm['name'].encode('utf8'), frm['email'].encode('utf8'),
                   frm['car'].encode('utf8'), frm['version'].encode('utf8'), frm['comment'].encode('utf8')
               )
            )
        newreport = True
    else:
        newreport = False
    return render_template('bug.html', bug=get_bug(bid), newreport=newreport)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
