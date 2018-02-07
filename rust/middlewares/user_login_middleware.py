# -*- coding: utf-8 -*-

from rust.core.exceptionutil import BusinessError
from rust.error_handlers.middleware_exception_handler import MiddlewareException
from rust.resources.business.user.user_repository import UserRepository

import settings

ERROR_CODE2TEXT = {
	'invalid session_key': u'session不合法',
	'expired session_key': u'session已过期，请重新登录',
}

class UserMiddleware(object):
	def process_request(sel, req, resp):
		"""
		检查用户登录状态
		请求中的cookie或者参数中需要带有正确的session_key
		session_key是在登录成功后，api返回给请求端的数据
		如果实在开发模式下，可以在请求中加入__dev_uid，表示user_id，即可无需加入session_key
		"""
		user = None
		UserRepository.set(user)

		if len(filter(lambda path: path in req.path, settings.NO_NEED_LOGIN_PATHS)) > 0:
			return

		session_key = req.cookies.get('__sid')
		if not session_key:
			session_key = req.params.get('__sid')
			if not session_key and settings.MODE == 'develop':
				user_id = req.params.get('__dev_uid')
				user = UserRepository().get_by_id(user_id)

		if session_key:
			try:
				user = UserRepository().get_by_session_key(session_key)
			except BusinessError, e:
				raise MiddlewareException(e.get_message(ERROR_CODE2TEXT))

		if user:
			req.context['user'] = user
			UserRepository.set(user)
		else:
			raise MiddlewareException(u'帐号不存在')