import numpy as np


class ExperimentTerminator():

    def __init__(self):

        # The number of samples to be used in Monte Carlo elements of the code. Increasing this number
        # improves accuracy of estimates at the expense of run time.
        self.mc_samples = 5_000

        # The Type I Error rate for the experiment. This determines the credible interval size used
        # for all calculations (e.g., alpha = 0.05 produces 95% credible intervals)
        self.alpha = 0.05

    def get_posterior_samples(self,
                              completed_trials_a,
                              completed_trials_b,
                              successes_a,
                              successes_b):
        """
        Get samples from the posterior distribution of the probability of success in the
        control group and the test group.

        :param completed_trials_a: Integer giving the number of trials completed in the control group
        :param completed_trials_b: Integer giving the number of trials completed in the test group
        :param successes_a: Integer giving the number of successes observed so far in the control group
        :param successes_b: Integer giving the number of successes observed so far in the test group

        :return: A list with two arrays of samples. The first array is a set of posterior samples from
            the distribution of the probability of success in the control group. The second array is the
            same for the test group.
        """

        posterior_samples_a = np.random.beta(successes_a,
                                             completed_trials_a - successes_a,
                                             self.mc_samples)
        posterior_samples_b = np.random.beta(successes_b,
                                             completed_trials_b - successes_b,
                                             self.mc_samples)
        return [posterior_samples_a, posterior_samples_b]

    def get_prob_reject_null(self,
                             planned_trials_a,
                             planned_trials_b,
                             completed_trials_a,
                             completed_trials_b,
                             successes_a,
                             successes_b,
                             posterior_samples_a,
                             posterior_samples_b):
        """
        Calculate the probability that the null hypothesis will be rejected by the planned end
        of the experiment

        :param planned_trials_a: Integer giving the number of trials planned to be completed in
                                 the control group in the experiment
        :param planned_trials_b: Integer giving the number of trials planned to be completed in 
                                 the test group in the experiment
        :param completed_trials_a: Integer giving the number of trials completed in the control group
        :param completed_trials_b: Integer giving the number of trials completed in the teest group
        :param successes_a: Integer giving the number of successes observed so far in the control group
        :param successes_b: Integer giving the number of successes observed so far in the test group
        :param posterior_samples_a: Posterior samples for the control group returned by get_posterior_samples
        :param posterior_samples_a: Posterior samples for the test group returned by get_posterior_samples

        :return: Float with the posterior predictive probability of rejecting the null hypothesis.
        """

        potential_successes_a = np.random.binomial(planned_trials_a - completed_trials_a,
                                                   posterior_samples_a,
                                                   self.mc_samples)
        potential_successes_a += successes_a
        potential_successes_b = np.random.binomial(planned_trials_b  - completed_trials_b,
                                                   posterior_samples_b,
                                                   self.mc_samples)
        potential_successes_b += successes_b

        rejection = np.zeros(self.mc_samples)
        for i in range(self.mc_samples):
            post_samples_a = np.random.beta(potential_successes_a[i] + 1,
                                            planned_trials_a - potential_successes_a[i] + 1,
                                            self.mc_samples)
            post_samples_b = np.random.beta(potential_successes_b[i] + 1,
                                            planned_trials_b - potential_successes_b[i] + 1,
                                            self.mc_samples)
            post_samples_b_minus_a = post_samples_b - post_samples_a
            interval = np.quantile(post_samples_b_minus_a, [self.alpha / 2, 1 - (self.alpha / 2)])
            if (interval[0] > 0 or interval[1] < 0):
                rejection[i] = 1

        return np.mean(rejection)

    def analyze_experiment(self,
                           planned_trials_a,
                           planned_trials_b,
                           completed_trials_a,
                           completed_trials_b,
                           successes_a,
                           successes_b):
        """
        Based on the number of planned trials, completed trials, and successes observed so far in the
        control and test groups, calculate a bunch of summary measures of the posterior distribution
        and predicted posterior.
        
        :param planned_trials_a: Integer giving the number of trials planned to be completed in
                                 the control group in the experiment
        :param planned_trials_b: Integer giving the number of trials planned to be completed in 
                                 the test group in the experiment
        :param completed_trials_a: Integer giving the number of trials completed in the control group
        :param completed_trials_b: Integer giving the number of trials completed in the teest group
        :param successes_a: Integer giving the number of successes observed so far in the control group
        :param successes_b: Integer giving the number of successes observed so far in the test group
        """

        posterior_samples = self.get_posterior_samples(completed_trials_a,
                                                    completed_trials_b,
                                                    successes_a,
                                                    successes_b)
        posterior_lift = (posterior_samples[1] - posterior_samples[0]) / posterior_samples[0]
        conversion_rate_a = successes_a / completed_trials_a
        conversion_rate_b = successes_b / completed_trials_b
        expected_lift = np.mean(posterior_lift)
        pr_b_gt_a = np.mean(posterior_lift >= 0)
        pr_reject_null = self.get_prob_reject_null(planned_trials_a,
                                                   planned_trials_b,
                                                   completed_trials_a,
                                                   completed_trials_b,
                                                   successes_a,
                                                   successes_b,
                                                   posterior_samples[0],
                                                   posterior_samples[1])
        return [conversion_rate_a,
                conversion_rate_b,
                expected_lift,
                pr_b_gt_a,
                pr_reject_null,
                posterior_lift]



if __name__ == "__main__":
    et = ExperimentTerminator()
    exp_outcomes = et.analyze_experiment(2000, 2000, 1000, 1000, 250, 270)
    print(exp_outcomes)