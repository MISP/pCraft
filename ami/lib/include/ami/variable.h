#ifndef _VARIABLE_H_
#define _VARIABLE_H_

#include <stddef.h>

#include "khash.h"

#ifdef __cplusplus
extern "C" {
#endif


enum _ami_variable_type_t {
	AMI_VAR_NONE,
	AMI_VAR_STR,
	AMI_VAR_INT,
	AMI_VAR_FLOAT,
	AMI_VAR_ARRAY,
	AMI_VAR_VARIABLE,
};
typedef enum _ami_variable_type_t ami_variable_type_t;
  
struct _ami_variable_t {
  ami_variable_type_t type;
  int    is_local;
  size_t len;
  char  *strval;
  int    ival;
  float  fval;
  struct _ami_variable_t *array;
};
typedef struct _ami_variable_t ami_variable_t;

KHASH_MAP_INIT_STR(varhash, ami_variable_t *)
  
ami_variable_t *ami_variable_new(void);
void ami_variable_set_int(ami_variable_t *var, int ival);
ami_variable_t *ami_variable_new_int(int ival);
void ami_variable_set_float(ami_variable_t *var, float fval);
ami_variable_t *ami_variable_new_float(float fval);
void ami_variable_set_string(ami_variable_t *var, char *strval);
  void ami_variable_set_variable(ami_variable_t *var, char *strval);
ami_variable_t *ami_variable_new_string(char *strval);
ami_variable_t *ami_variable_new_variable(char *strval);
ami_variable_t *ami_variable_array_append(ami_variable_t *var, ami_variable_t *to_append);
ami_variable_t *ami_variable_array_get_at_index(ami_variable_t *array, size_t index);
ami_variable_t *ami_variable_copy(ami_variable_t *var);
void ami_variable_debug(ami_variable_t *var);
char *ami_variable_to_string(ami_variable_t *var);
int ami_variable_to_int(ami_variable_t *var);
void ami_variable_free(ami_variable_t *var);
void ami_variable_make_local(ami_variable_t *var);
  
#ifdef __cplusplus
}
#endif

#endif // _VARIABLE_H_
