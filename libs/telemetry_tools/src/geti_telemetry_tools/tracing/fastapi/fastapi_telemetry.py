# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

"""Helpers for the integration of OpenTelemetry with FastAPI"""

import logging

from opentelemetry.trace.span import Span  # type: ignore[attr-defined]

from geti_telemetry_tools.tracing.common import tracer_provider
from geti_telemetry_tools.tracing.propagation import HttpEncodedHeaderSetter, propagator

logger = logging.getLogger(__name__)


class FastAPITelemetry:
    """OpenTelemetry instrumentation for FastAPI"""

    @staticmethod
    def instrument(app) -> None:  # noqa: ANN001
        """
        Instrument a FastAPI application.

        The instrumentor wraps a FastAPI application and creates tracing context on
        incoming HTTP requests.

        By means of a response hook, the trace ID is returned to the client through
        the 'X-Request-ID' response header.

        :param app: FastAPI application to instrument
        """
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore[attr-defined]
        except ImportError:
            logger.exception(
                "Cannot instrument FastAPI because opentelemetry-instrumentation-fastapi "
                "is not installed. Add 'telemetry[fastapi]' to the required packages."
            )
            raise

        def response_hook(span: Span, message: dict) -> None:
            if span and span.is_recording() and message.get("type") == "http.response.start":
                propagator.inject(
                    setter=HttpEncodedHeaderSetter(),  # type: ignore[arg-type]
                    carrier=message["headers"],
                )

        logger.debug("Instrumenting FastAPI application")
        FastAPIInstrumentor().instrument_app(app, tracer_provider=tracer_provider, client_response_hook=response_hook)

    @staticmethod
    def uninstrument(app) -> None:  # noqa: ANN001
        """
        Uninstrument a FastAPI application.

        :param app: FastAPI application to instrument
        """
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore[attr-defined]
        except ImportError:
            logger.exception(
                "Cannot instrument FastAPI because opentelemetry-instrumentation-fastapi "
                "is not installed. Add 'telemetry[fastapi]' to the required packages."
            )
            raise

        logger.debug("Uninstrumenting FastAPI application")
        FastAPIInstrumentor().uninstrument_app(app)
