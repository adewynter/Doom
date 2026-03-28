# These were the ones used in the original GPT-4 paper
legacy_agent_params_legacy = {"temperature": 0.9,
                              "max_tokens": 25,
                              "top_p": 1
                             }
legacy_planner_params = {"temperature": 0.1,
                         "top_p": 1, 
                         "max_tokens": 150
                        }
legacy_vision_params = {"temperature": 0.1,
                        "top_p": 1,
                        "max_tokens": 1500
                        }
legacy_expert_params = {"expert1": {"temperature": 0.9, "max_tokens": 25, "top_p": 1},
                        "expert2": {"temperature": 0.9, "max_tokens": 25, "top_p": 1},
                        "expert3": {"temperature": 0.9, "max_tokens": 25, "top_p": 1}
                        }

# For OpenAI RLM models
openai_rlm_agent_params = {"max_completion_tokens": 256}
openai_rlm_planner_params = {"max_completion_tokens": 512}
openai_rlm_vision_params = {"max_completion_tokens": 1500} 
openai_rlm_expert_params = {"expert1": {"max_completion_tokens": 256},
                            "expert2": {"max_completion_tokens": 256},
                            "expert3": {"max_completion_tokens": 256}
                            }

# For nice models
actually_open_rlm_agent_params = {"max_tokens": 256}
actually_open_rlm_planner_params = {"max_tokens": 512}
actually_open_rlm_vision_params = {"max_tokens": 1500} 
actually_open_rlm_expert_params = {"expert1": {"max_tokens": 256},
                                   "expert2": {"max_completion_tokens": 256},
                                   "expert3": {"max_completion_tokens": 256}
                                  }
