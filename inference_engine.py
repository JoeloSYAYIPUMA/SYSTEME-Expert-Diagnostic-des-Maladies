"""
Moteur d'inference a chainage avant pour le systeme expert agricole
"""


class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.working_memory = []  # Faits derives
        self.triggered_rules = []  # Regles declenchees
        self.conclusions = {
            'diagnostics': [],
            'alertes': [],
            'traitements': [],
            'conseils': [],
            'informations': [],
        }

    def match_condition(self, condition_key, condition_value, facts):
        """
        Verifie si une condition specifique est satisfaite
        Gere les valeurs uniques, les listes, et les operateurs speciaux
        """
        if condition_key not in facts:
            return False

        fact_value = facts[condition_key]

        # Si fact_value est None, condition non satisfaite
        if fact_value is None:
            return False

        # Si la condition est une liste (plusieurs valeurs possibles)
        if isinstance(condition_value, list):
            if isinstance(fact_value, list):
                # Verifier s'il y a une intersection
                return any(v in condition_value for v in fact_value)
            return fact_value in condition_value

        # Si la condition est une valeur unique
        if isinstance(fact_value, list):
            return condition_value in fact_value
        return fact_value == condition_value

    def evaluate_rule(self, rule, facts):
        """
        Evalue si une regle s'applique avec les faits actuels
        """
        conditions = rule['conditions']

        # Verifier toutes les conditions
        for key, value in conditions.items():
            if not self.match_condition(key, value, facts):
                return False

        return True

    def apply_actions(self, rule):
        """
        Applique les actions d'une regle declenchee
        """
        for action in rule['actions']:
            action_type = action.get('type')

            if action_type == 'diagnostic':
                self.conclusions['diagnostics'].append(
                    {
                        'maladie': action['maladie'],
                        'probabilite': action['probabilite'],
                        'regle': rule['id'],
                    }
                )

            elif action_type == 'alerte':
                self.conclusions['alertes'].append({'message': action['message'], 'regle': rule['id']})

            elif action_type == 'alerte_epidemio':
                self.conclusions['alertes'].append(
                    {
                        'type': 'epidemiologique',
                        'message': action['message'],
                        'risque': action['risque'],
                        'action_preventive': action['action_preventive'],
                        'regle': rule['id'],
                    }
                )

            elif action_type == 'traitement':
                # Chercher si un diagnostic existe deja pour ajouter le traitement
                existing_treatment = next(
                    (
                        t
                        for t in self.conclusions['traitements']
                        if t.get('maladie') == action.get('maladie', 'general')
                    ),
                    None,
                )

                if not existing_treatment:
                    self.conclusions['traitements'].append(
                        {
                            'maladie': action.get('maladie', 'general'),
                            'stade': action.get('stade', 'tous'),
                            'recommandation': action['recommandation'],
                            'regle': rule['id'],
                        }
                    )

            elif action_type == 'recommandation':
                self.conclusions['traitements'].append(
                    {'type': 'recommandation', 'message': action['message'], 'regle': rule['id']}
                )

            elif action_type == 'conseil':
                self.conclusions['conseils'].append({'message': action['message'], 'regle': rule['id']})

            elif action_type == 'conseil_long_terme':
                self.conclusions['conseils'].append(
                    {'type': 'long_terme', 'message': action['message'], 'regle': rule['id']}
                )

            elif action_type == 'conseil_prevention':
                self.conclusions['conseils'].append(
                    {'type': 'prevention', 'message': action['message'], 'regle': rule['id']}
                )

        # Marquer la regle comme declenchee
        self.triggered_rules.append(rule['id'])

    def forward_chaining(self, facts):
        """
        Moteur d'inference a chainage avant
        """
        # Reinitialiser les conclusions
        self.working_memory = []
        self.triggered_rules = []
        self.conclusions = {
            'diagnostics': [],
            'alertes': [],
            'traitements': [],
            'conseils': [],
            'informations': [],
        }

        rules = self.kb.get_rules()
        new_facts_added = True

        # Chainage avant iteratif
        iteration = 0
        max_iterations = 10  # Eviter les boucles infinies

        while new_facts_added and iteration < max_iterations:
            new_facts_added = False
            iteration += 1

            for rule in rules:
                # Ne pas reappliquer les regles deja declenchees
                if rule['id'] in self.triggered_rules:
                    continue

                # Evaluer la regle
                if self.evaluate_rule(rule, facts):
                    print(f"Regle declenchee: {rule['id']} - {rule['name']}")
                    self.apply_actions(rule)
                    new_facts_added = True

        # Ajouter les informations detaillees sur les maladies diagnostiquees
        for diag in self.conclusions['diagnostics']:
            maladie = diag['maladie']
            info = self.kb.get_maladie_info(maladie)
            if info:
                self.conclusions['informations'].append({'maladie': maladie, 'details': info})

        return self.conclusions

    def get_explanation(self):
        """Retourne une explication du raisonnement"""
        explanation = "Raisonnement du systeme expert:\n"
        explanation += f"Regles declenchees: {', '.join(self.triggered_rules)}\n"

        if self.conclusions['diagnostics']:
            explanation += "\nDiagnostics poses:\n"
            for diag in self.conclusions['diagnostics']:
                explanation += f"- {diag['maladie']} (probabilite: {diag['probabilite']*100}%)\n"

        return explanation
