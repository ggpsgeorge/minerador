from models import Feature, Method, ScenarioOutline, SimpleScenario, Repository
from base_execution import BaseExecution
import json
import os
import sys
import linecache
import subprocess
import json

class ViewModel(BaseException):

    def __init__(self, token):
        self.token = token
        self.class_definition_line = None
        self.method_definition_lines = []

        self.feature = Feature()


    # Funcao retorna o json da pagina
    def get_json(self, url):
        resp = os.popen("curl -H 'Authorization: token " + self.token + "' " + url).read()
        return json.loads(resp)


    # Funcao que retorna uma lista com as urls de todos os repo do usuario
    def get_repo(self, url):
        repo_urls = []

        data = self.get_json(url)

        for repo in data:
            repo_urls.append(repo['url'] + '/contents')

        return repo_urls


    # Funcao que procura a extensao e retorna para os casos que a extensao seja a correta ou nao
    def find_ext(self, string1, ext):
        lis_string = string1.split('.')
        tam = len(lis_string)

        if tam >= 2:
            if lis_string[tam - 1] == ext:
                return 1
            else:
                return 0
        else:
            return 0

    # Funcao que faz o download dos arquivos em dirs e subdirs com uma extensao especifica
    def download_files(self, url, extensao):

        dir_urls = []

        data = self.get_json(url)

        for raw in data:

            if self.find_ext(raw['name'], extensao):
                file = open("dados/" + raw['name'], 'w')
                file.write(os.popen("curl -H 'Authorization: token " + self.token + "' "
                                    + raw['download_url']).read())
                file.close()
            if raw['type'] == "dir":
                dir_urls.append(raw['url'])

        if dir_urls != []:
            for dir in dir_urls:
                self.download_files(dir, extensao)


    # gets an object repository using its url as parameter
    def getRepositoryFromPath(self, path):
        repositoryJson = self.get_json(path)
        ownerJson = self.get_json(repositoryJson['owner']['url'])
        repository = Repository()
        repository.path = repositoryJson['url']
        repository.name = repositoryJson['name']
        repository.owner = repositoryJson['owner']['login']
        repository.country = ownerJson['location']
        repository.language = repositoryJson['language']

        # now getting the projects features
        self.download_files(repository.path + '/contents', "feature")

        return repository

    #========================================================

    # this method will execute all the features at this project
    def execute(self):
        pass

    # this method will execute only a specific feature
    def execute_feature(self, feature_name):
        """This method will execute only a specific feature
        :param feature_name: define the feature that will be executed
        :return: a json file with the trace.
        """
        pass

    # this method will execute a specific scenario into a specific feature
    # filename: refer to the .feature file
    # scenario_ref: refer to the line or the name of a specific scenario
    def execute_scenario(self, feature_name, scenario_ref):
        """This Method will execute only a specific scenario
        :param feature_name: define the feature that contains this scenario
        :param scenario_ref: contains a key to get a scenario
        :return: a json file with the trace.
        """
        subprocess.call(['rails', 'cucumber', feature_name])
        self.get_feature_information(feature_name)

        with open('coverage/cucumber/.resultset.json') as f:
            json_data = json.load(f)
            for k in json_data:
                for i in json_data[k]['coverage']:
                    json_data[k]['coverage'][i]
                    self.run_file(i, json_data[k]['coverage'][i])

        self.export_json()

    def run_file(self, filename, cov_result):
        """This method will execute a specific feature file
        :param filename: the  name of the feature file
        :param cov_result: a array containing the result os simpleCov for some method
        :return: Instantiate the Methods executed.
        """
        self.method_definition_lines = []
        with open(filename) as file:
            if self.is_empty_class(file):
                return

            self.get_class_definition_line(file)
            self.get_method_definition_lines(file, cov_result)
            self.remove_not_executed_definitions(filename, cov_result)

            for method in self.method_definition_lines:
                new_method = Method()
                new_method.method_name = self.get_method_or_class_name(method, filename)
                new_method.class_name = self.get_method_or_class_name(self.class_definition_line, filename)
                new_method.class_path = filename
                self.feature.scenarios[0].executed_methods.append(new_method)

    def is_method(self, line):
        """Verify if is the line is a method definition.
        :param line: Line content.
        :return: True if is a method definition, False if not.
        """
        # We only want the first token in the line, to avoid false positives.
        # That is, the word 'def' appearing in some other context.
        tokens = line.split()
        if tokens:
            first_token = tokens[0]
            return first_token == 'def'
        return False

    def is_class(self, line):
        """Verify if this line is a class definition.
        :param line: Line content.
        :return: true if is a class, false if not.
        """
        # We only want the first token in the line, to avoid false positives.
        # That is, the word 'class' appearing in some other context.
        tokens = line.split()
        if tokens:
            first_token = tokens[0]
            return first_token == 'class'
        return False

    def get_method_or_class_name(self, line_number, filename):
        """Method that get the name of Methods and Classes
        :param line_number: the number of the line.
        :param filename: the file that contains this line.
        :return: String Name.
        """
        line = linecache.getline(filename, line_number)

        # The method or class name is always going to be the second token
        # in the line.
        name_token = line.split()[1]

        # If the method definition contains parameters, part of it will also
        # be in the token though. For example:
        #    def foo(x, y)
        # would become 'foo(x,'. We then separate those parts.
        name, parenthesis, rest = name_token.partition('(')

        return name

    def get_class_definition_line(self, file):
        """This method get the line where a class is defined.
        :param file: the file that contains this class.
        :return: the number of the line.
        """
        file.seek(0)
        for line_number, line in enumerate(file, 1):
            if self.is_class(line):
                self.class_definition_line = line_number
                return

    def get_method_definition_lines(self, file, cov_result):
        """This method get the line where a method is defined.
        :param file: The file that contains this method.
        :param cov_result: .
        :return: the number of the line.
        """
        file.seek(0)
        for line_number, line in enumerate(file, 1):
            if self.is_method(line):
                self.method_definition_lines.append(line_number)

    def remove_not_executed_definitions(self, filename, cov_result):
        """Remote all definitions that was not executed.
        :param filename: the file that contains this definitions.
        :param cov_result: json containing the simpleCov result.
        :return: definitions removed.
        """
        # Methods that weren't executed aren't relevant, so we remove them here.
        for line in self.method_definition_lines:
            if not self.was_executed(line, filename, cov_result):
                self.method_definition_lines.remove(line)

    def was_executed(self, def_line, filename, cov_result):
        """Verify if a definitions was executed.
        :param def_line: Line of a definition.
        :param filename: the file that contains this definition.
        :param cov_result: simpleCov json result.
        :return: True if was executed, and False if not.
        """
        # We go through the file from the line containing the method definition
        # until its matching 'end' line. We need to keep track of the 'end'
        # keyword appearing in other contexts, e.g. closing other blocks of code.
        remaining_blocks = 1
        current_line = def_line

        block_tokens = ['do', 'if', 'case', 'for', 'begin', 'while']

        while remaining_blocks:
            line = linecache.getline(filename, current_line)
            tokens = line.split()
            # If we have a line that requires a matching 'end', we increase the
            # number of blocks.
            if any(token in tokens for token in block_tokens):
                remaining_blocks += 1
            # Likewise, if we found an 'end', we decrease the number of blocks.
            # When it gets to zero, that means we have reached the end of the
            # method.
            if 'end' in tokens:
                remaining_blocks -= 1
            current_line += 1

        end_line = current_line - 1

        for line in range(def_line, end_line):
            if cov_result[line]:
                return True
        return False

    def is_empty_class(self, file):
        """Verify if a class is empty
        :param file: file that will be analysed.
        :return: True if is empty, and False if not.
        """
        file.seek(0)
        for line in file:
            if self.is_method(line):
                return False
        return True

    def get_feature_information(self, path):
        """Get all information in a .feature file.
        :param path: the path of the .feature file.
        :return: feature information instantiated.
        """

        self.get_language(path)
        self.feature.path_name = path
        self.get_feature_name(path)
        self.get_scenarios(path)
        self.get_steps(path)

    def get_feature_name(self, path):
        """This method get the feature name.
        :param path: the path to this feature file.
        :return: the name of the feature.
        """
        with open(path) as file:
            file.seek(0)
            for line_number, line in enumerate(file, 1):
                if "Funcionalidade: " in line:
                    self.feature.feature_name = line.split("Funcionalidade: ", 1)[1].replace('\n', '')
        return

    def get_scenarios(self, path):
        """This method get all scenarios of a feature.
        :param path: the path to the feature file.
        :return: all scenarios instantiated.
        """
        with open(path) as file:
            file.seek(0)
            for line_number, line in enumerate(file, 1):
                if "Cenario: " in line:
                    # print ("Cenario: " + line.split("Delineacao do Cenario: ",1)[1])
                    new_scenario = SimpleScenario()
                    new_scenario.scenario_title = line.split("Cenario: ", 1)[1].replace('\n', '')
                    new_scenario.line = line_number
                    self.feature.scenarios.append(new_scenario)
        return

    def get_steps(self, path):
        """This method get all steps into each scenario of a feature.
        :param path: the path to the feature file.
        :return: all steps instantiated.
        """
        qt_scenarios = len(self.feature.scenarios)
        key_words = ["Quando ", "E ", "Dado ", "Entao "]
        current_scenario = 0

        with open(path) as file:
            file.seek(0)
            for line_number, line in enumerate(file, 1):
                if any(word in line for word in key_words):
                    self.feature.scenarios[current_scenario].steps.append(line.replace('\n', ''))

                    if "Entao " in line:
                        current_scenario += 1
        return

    def get_language(self, path):
        """Get the language of the .feature file.
        :param path: the path to the .feature file.
        :return: language.
        """
        with open(path) as file:
            file.seek(0)
            for line_number, line in enumerate(file, 1):
                if "#language:" in line:
                    self.feature.language = line.split("#language:", 1)[1].replace('\n', '')
        return

    def export_json(self):
        """This method will export all data to a json file.
        :return: json file.
        """
        file = open(self.feature.feature_name + '_result.json', 'w')

        file.write(self.feature.toJSON())
