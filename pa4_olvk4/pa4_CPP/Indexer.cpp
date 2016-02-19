#include "Indexer.h"

#include <fstream>
#include <iostream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <utility>

using namespace std;

// Reads content from the supplied input file stream, and transforms the
// content into the actual on-disk inverted index file.

// input: captions file
// output: inverted index file
// case insensitive
// include only alphabetical words and ignore any other symbols

Indexer::Indexer(){
	ifstream stop_words_file;
	stop_words_file.open("english.stop");
	if(!stop_words_file.is_open()){
		cerr << "Stop Words file failed to open" << endl;
		exit(1);
	}
	string word;
	while(stop_words_file >> word){
		stop_words.insert(word);
	}
}

void Indexer::index(ifstream& content, ostream& outfile)
{
	// Read from file
	string line;
	int docid = 1;
	while(content.good()){
		getline(content, line);
		
		// skip work if newline at end of file
		if(line.size() == 0){
			break;
		}

		// remove garbage characters
		line.erase(remove_if(line.begin(), line.end(), 
			[](char c){return !isalnum(c) && !isspace(c);}), line.end());
		
		// convert line to lowercase
		for(char &c : line){
			c = tolower(c);
		}

		string word;
		stringstream tmp_ss;
		stringstream ss;

		tmp_ss << line;
		while(tmp_ss >> word){
			// don't do anything if we are reading a stopword
			if(stop_words.find(word) != stop_words.end()){
				continue;
			}

			ss << word << " ";

			word_map[word].docid_map[docid]++;
			word_map[word].total_num_occur++;
		}

		docs_c.emplace_back(ss.str());
		
		docid++;
	}

	docid--;

	int num_docs = docid;

	// each word must have an idf
	for(auto &word_pair : word_map){
		double idf = log10(double(num_docs)/double(word_pair.second.docid_map.size()));
		cout << "idf for word " << word_pair.first << " is " << idf << endl;
		word_pair.second.idf = idf;
	}

	// each docid must have a normalization factor before sqrt
	for(int i=0; i<num_docs; i++){
		stringstream ss;
		ss << docs_c[i].doc_data;
		string word;
		double norm_factor = 0;

		while(ss >> word){
			// add squares of idfs for each word
			// cout << "word " << word << " and docid " << i+1 << "\n";
			norm_factor += word_map[word].idf * word_map[word].idf
				* word_map[word].docid_map[i+1] * word_map[word].docid_map[i+1];
		}

		docs_c[i].normalization_factor = norm_factor;
		cout << "doc norm factor for doc " << i+1 << " is " << norm_factor << "\n";
	}

	for(auto &word_pair : word_map){
		outfile << word_pair.first << " " << word_pair.second.idf << " "
			<< word_pair.second.total_num_occur;

		// go through vector of docids, outputting docid, #occur, doc's norm fac
		for(auto &docid_pair : word_pair.second.docid_map){
			outfile << " " << docid_pair.first << " " << docid_pair.second << 
				 " " << docs_c[docid_pair.first-1].normalization_factor;
		}
		outfile << endl;
	}

	cout << "indexing finished" << endl;
}