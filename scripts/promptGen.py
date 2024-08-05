### PROMPT GENERATION
#
# Classes for prompt engineering. Builds a prompt generator with the 
# input distribution and randomly pick one prompt. 
#
##############################

import random

class PromptSetting():
    def __init__(self, name:str, options, weights:list=[]):
        self.name = name

        if isinstance(options,dict):
            self.options_names   = list(options.keys())
            self.options_weights = list(options.values())
        
        elif isinstance(options,list) and weights :
            self.options_names   = options
            self.options_weights = weights
        
        else : 
            raise TypeError("'options' must be a dict or a list, and if it's a list, weights can't be empty")

    def __repr__(self):
        string = ['   - ' + str(self.options_weights[i]).ljust(4) + ' ' + self.options_names[i] for i in range(len(self.options_names))]
        return self.name + " options : \n" + '\n'.join(string)

    def __getitem__(self,indx):
        return self.options_names[indx]

    def random_pick(self):
        return random.choices(self.options_names,self.options_weights)[0]

class PromptGenerator():
    def __init__ (
        self,
        options:list,
        positive_const     = ['photography', '4k', 'highly detailed', 'sharp focus', 'distinct from background'], 
        negative_const     = ['mouth', 'lips', 'tiling',  'poorly drawn face', 'out of frame', 'extra limbs', 'disfigured', 'deformed', 'body out of frame', 'bad anatomy', 'watermark', 'signature', 'cut ox', 'low contrast', 'bad art', 'beginner', 'amateur', 'distorted face', 'blurry', 'dray', 'grainy', 'blending']   
        ):

        self.options           = options
        self.positive_const    = positive_const
        self.negative_const    = negative_const

    def __repr__(self):
        output_str      = " --- Prompt Generator --- \n"
        settings_str    = '\n'.join([option.__repr__() for option in self.options])
        
        return output_str+settings_str

    def random_pick(self):
        positive_choices = ""

        for option in self.options : 
            positive_choices += option.random_pick() + ', '

        positive_prompt     = '' + positive_choices + ', '.join(self.positive_const)
        negative_prompt     = ', '.join(self.negative_const)

        return positive_prompt,negative_prompt

#####################################
# TEST SECTION

if __name__=='__main__':

    options = [
        PromptSetting('Gender',{'man':0.5,'woman':0.5}), 
        PromptSetting('Hair Color',{'auburn hair':0.05,'dark hair':0.3, 'dark blond hair':0.3, 'blond hair':0.2,'white hair':0.1,'bald':0.05}),
        PromptSetting('Clothes',{'casual clothes':0.5, 'colorful clothes':0.2, 'classy clothes':0.2, 'random clothes':0.1}),
        PromptSetting('Background',{'city background':0.18, 'sky background':0.18, 'landscape background':0.18, 'crop field background':0.18, 'mountain background':0.18, 'random background':0.10})
    ]

    prompt = PromptGenerator(options=options)  
    print(prompt)
    print(prompt.random_pick())
    print(prompt.random_pick())
    print(prompt.random_pick())

    background      = PromptSetting('Background',{'city background':0.18, 'sky background':0.18, 'landscape background':0.18, 'crop field background':0.18, 'mountain background':0.18, 'random background':0.10})

    print(background)
