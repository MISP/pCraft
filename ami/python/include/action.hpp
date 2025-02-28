#ifndef _ACTIONPP_H_
#define _ACTIONPP_H_

#include <map>
#include <vector>

#include <ami/action.h>

class Action {
public:
  Action(void);
  ~Action(void);
  void set_name(char *_name) { name = _name;};
  char *get_name(void) { return name;};
  void set_exec(char *_exec) { exec = _exec;};
  char *get_exec(void) { return exec;};
  std::map<std::string, std::string> get_variables(void) { return variables; };
  void set_variable(std::string varname, std::string varvalue) { variables[varname] = varvalue; };
  std::map<std::string, std::string> variables;
  std::map<std::string, float> sleep_group;
  std::map<std::string, float> get_sleep_group(void) { return sleep_group; };
  std::vector<std::string> get_local_variables(void) { return local_variables; };
  std::vector<std::string> local_variables;

  std::map<std::string, std::map<std::string, std::map<std::string, std::string>>> field_actions;
  std::map<std::string, std::map<std::string, std::map<std::string, std::string>>> get_field_actions(void) { return field_actions; };
  float GetSleepCursor(void) { return sleep_cursor; };
  void SetSleepCursor(float new_sleep_cursor) { sleep_cursor = new_sleep_cursor;};  
  float sleep_cursor;
  size_t GetRepeatIndex(void) { return repeat_index; };
  size_t repeat_index;
private:
  ami_action_t *_action;
  char *name;
  char *exec;
};

#endif // _ACTIONPP_H_
